import json
import hmac
import hashlib
import razorpay
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required

from .models import Category, Book, Cart, CartItem, Order, OrderItem, Wishlist
from .google_books import search_google_books


# ─── Helpers ────────────────────────────────────────────────────────────────

def get_or_create_cart(request):
    """Get or create a cart, preferring user-linked cart when authenticated.
    When a user logs in, Django rotates the session key — so we must look up
    by user first to avoid showing an empty new cart when one already exists.
    """
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        # Try to get the user's cart by user FK first
        user_cart = Cart.objects.filter(user=request.user).first()
        session_cart = Cart.objects.filter(session_key=session_key).exclude(
            user=request.user
        ).first()

        if user_cart and session_cart:
            # Merge session cart items into user cart, then delete session cart
            for item in session_cart.items.all():
                existing = user_cart.items.filter(book=item.book).first()
                if existing:
                    existing.quantity += item.quantity
                    existing.save()
                else:
                    item.cart = user_cart
                    item.save()
            session_cart.delete()
            return user_cart

        if user_cart:
            # Make sure session_key stays current
            if user_cart.session_key != session_key:
                user_cart.session_key = session_key
                user_cart.save()
            return user_cart

        if session_cart:
            # Attach this session cart to the logged-in user
            session_cart.user = request.user
            session_cart.session_key = session_key
            session_cart.save()
            return session_cart

        # No cart at all — create one linked to user
        cart, _ = Cart.objects.get_or_create(
            session_key=session_key,
            defaults={'user': request.user}
        )
        if not cart.user:
            cart.user = request.user
            cart.save()
        return cart

    # Guest: session-based only
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


# ─── Home ────────────────────────────────────────────────────────────────────

@ensure_csrf_cookie
def home(request):
    categories = Category.objects.all()

    # Attach a real book cover to each category for the slider card background
    for cat in categories:
        # Prefer a book with a real scanned cover (edge=curl), fall back to any cover
        sample = (
            cat.books.filter(cover_image_url__contains='edge=curl').order_by('-rating').first()
            or cat.books.exclude(cover_image_url='').order_by('-rating').first()
        )
        cat.sample_cover = sample.cover_image_url if sample else ''

    featured_books = Book.objects.filter(is_featured=True).select_related('category')[:12]
    bestsellers = Book.objects.filter(is_bestseller=True).select_related('category')[:6]

    # Carousel: prefer books with real scanned covers (edge=curl)
    carousel_books = Book.objects.filter(
        cover_image_url__contains='edge=curl',
        rating__gte=3.5
    ).select_related('category').order_by('-rating', '-is_bestseller')[:20]

    # Fallback 1: zoom=2 covers
    if carousel_books.count() < 5:
        carousel_books = Book.objects.filter(
            cover_image_url__startswith='https',
            cover_image_url__contains='zoom=2',
        ).select_related('category').order_by('-rating')[:20]

    # Fallback 2: any book with ANY cover URL
    if carousel_books.count() < 5:
        carousel_books = Book.objects.exclude(
            cover_image_url=''
        ).select_related('category').order_by('-rating')[:20]

    context = {
        'categories': categories,
        'featured_books': featured_books,
        'bestsellers': bestsellers,
        'carousel_books': carousel_books,
    }
    return render(request, 'store/home.html', context)


# ─── Category ────────────────────────────────────────────────────────────────

def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    books_qs = Book.objects.filter(category=category).order_by('-created_at')

    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        books_qs = books_qs.order_by('price')
    elif sort == 'price_desc':
        books_qs = books_qs.order_by('-price')
    elif sort == 'rating':
        books_qs = books_qs.order_by('-rating')
    elif sort == 'title':
        books_qs = books_qs.order_by('title')

    paginator = Paginator(books_qs, 16)
    page = request.GET.get('page', 1)
    books = paginator.get_page(page)

    all_categories = Category.objects.all()
    context = {
        'category': category,
        'books': books,
        'all_categories': all_categories,
        'current_sort': sort,
    }
    return render(request, 'store/category.html', context)


# ─── Book Detail ──────────────────────────────────────────────────────────────

def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    related_books = Book.objects.filter(category=book.category).exclude(pk=book.pk)[:4]
    is_wishlisted = (
        request.user.is_authenticated and
        Wishlist.objects.filter(user=request.user, book=book).exists()
    )
    context = {
        'book': book,
        'related_books': related_books,
        'is_wishlisted': is_wishlisted,
    }
    return render(request, 'store/book_detail.html', context)


# ─── All Books ────────────────────────────────────────────────────────────────

def book_list_view(request):
    books_qs = Book.objects.select_related('category').order_by('-rating')
    paginator = Paginator(books_qs, 24)
    books = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'store/book_list.html', {
        'books': books,
        'categories': Category.objects.all(),
    })


# ─── Search ───────────────────────────────────────────────────────────────────

def search_view(request):
    query = request.GET.get('q', '').strip()
    books = []
    if query:
        # 1. Find books already in DB
        db_books = list(Book.objects.filter(
            Q(title__icontains=query) | Q(authors__icontains=query)
        ).select_related('category')[:12])

        # 2. If not enough, fetch from Google Books and auto-save into DB
        if len(db_books) < 6:
            api_items = search_google_books(query, max_results=12)
            for item in api_items:
                gid = item.get('id')
                if not gid:
                    continue
                # Don't duplicate if already in DB
                if Book.objects.filter(google_books_id=gid).exists():
                    continue
                # Get or create a matching category
                cat_name = item.get('category', 'General')
                category, _ = Category.objects.get_or_create(
                    name=cat_name,
                    defaults={'slug': slugify(cat_name), 'icon': '📚'}
                )
                try:
                    Book.objects.create(
                        google_books_id=gid,
                        title=item['title'],
                        authors=item['authors'],
                        cover_image_url=item.get('cover', ''),
                        description=item.get('description', ''),
                        price=item['price'],
                        rating=item['rating'],
                        category=category,
                        stock=50,
                    )
                except Exception:
                    pass  # slug collision or other edge-case — skip silently

        # Re-query so we pick up newly saved books too
        books = list(Book.objects.filter(
            Q(title__icontains=query) | Q(authors__icontains=query)
        ).select_related('category')[:24])

    context = {
        'query': query,
        'books': books,
    }
    return render(request, 'store/search.html', context)


# ─── Cart ─────────────────────────────────────────────────────────────────────

def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('book').all()
    context = {'cart': cart, 'items': items}
    return render(request, 'store/cart.html', context)


def cart_json(request):
    """Return cart data as JSON for the drawer — uses user-aware cart lookup."""
    cart = get_or_create_cart(request)  # uses user FK if logged in
    if not cart:
        return JsonResponse({'items': [], 'total': '0.00', 'count': 0})

    items = []
    for item in cart.items.select_related('book').all():
        items.append({
            'id': item.pk,
            'book_id': item.book.pk,
            'title': item.book.title,
            'authors': item.book.authors,
            'cover': item.book.get_cover(),
            'price': str(item.book.price),
            'quantity': item.quantity,
            'subtotal': str(item.subtotal),
            'slug': item.book.slug,
        })
    return JsonResponse({
        'items': items,
        'total': str(cart.total),
        'count': cart.item_count,
    })


@require_POST
def add_to_cart(request, book_id):
    if request.user.is_authenticated and (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')):
        return JsonResponse({'success': False, 'message': 'Admin accounts cannot make purchases.'}, status=403)
        
    book = get_object_or_404(Book, pk=book_id)
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        item.quantity += 1
        item.save()
    return JsonResponse({
        'success': True,
        'cart_count': cart.item_count,
        'message': f'"{book.title}" added to cart!',
    })


@require_POST
def remove_from_cart(request, item_id):
    if not request.session.session_key:
        return JsonResponse({'success': False}, status=400)
    item = get_object_or_404(CartItem, pk=item_id, cart__session_key=request.session.session_key)
    item.delete()
    cart = get_or_create_cart(request)
    return JsonResponse({
        'success': True,
        'cart_count': cart.item_count,
        'cart_total': str(cart.total),
    })


@require_POST
def update_cart(request, item_id):
    if not request.session.session_key:
        return JsonResponse({'success': False}, status=400)
    item = get_object_or_404(CartItem, pk=item_id, cart__session_key=request.session.session_key)
    data = json.loads(request.body)
    qty = int(data.get('quantity', 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    cart = get_or_create_cart(request)
    return JsonResponse({
        'success': True,
        'subtotal': str(item.subtotal) if qty >= 1 else '0',
        'cart_count': cart.item_count,
        'cart_total': str(cart.total),
    })


# ─── Buy Now (Add to cart + redirect to checkout) ────────────────────────────

@login_required
@require_POST
def buy_now(request, book_id):
    if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'):
        from django.contrib import messages
        messages.error(request, 'Admin accounts cannot make purchases.')
        return redirect('home')
        
    book = get_object_or_404(Book, pk=book_id)
    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('checkout')


# ─── Checkout ────────────────────────────────────────────────────────────────

@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    if cart.item_count == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    razorpay_client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    amount_paise = int(cart.total * 100)

    if request.method == 'POST':
        rz_order = razorpay_client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': '1',
        })
        request.session['checkout_data'] = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'pincode': request.POST.get('pincode'),
            'razorpay_order_id': rz_order['id'],
            'amount': str(cart.total),
        }
        return JsonResponse({
            'razorpay_order_id': rz_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': amount_paise,
            'currency': 'INR',
            'name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
        })

    context = {
        'cart': cart,
        'items': cart.items.select_related('book').all(),
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'store/checkout.html', context)


@csrf_exempt
@require_POST
def payment_success(request):
    data = json.loads(request.body)
    payment_id = data.get('razorpay_payment_id')
    order_id = data.get('razorpay_order_id')
    signature = data.get('razorpay_signature')

    # Verify signature
    key_secret = settings.RAZORPAY_KEY_SECRET.encode()
    message = f"{order_id}|{payment_id}".encode()
    generated_sig = hmac.new(key_secret, message, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(generated_sig, signature):
        return JsonResponse({'success': False, 'error': 'Invalid payment signature'}, status=400)

    checkout_data = request.session.get('checkout_data', {})
    cart = get_or_create_cart(request)

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
        razorpay_order_id=order_id,
        razorpay_payment_id=payment_id,
        razorpay_signature=signature,
        full_name=checkout_data.get('full_name', ''),
        email=checkout_data.get('email', ''),
        phone=checkout_data.get('phone', ''),
        address=checkout_data.get('address', ''),
        city=checkout_data.get('city', ''),
        state=checkout_data.get('state', ''),
        pincode=checkout_data.get('pincode', ''),
        total=Decimal(checkout_data.get('amount', '0')),
        status='paid',
    )

    for item in cart.items.select_related('book').all():
        OrderItem.objects.create(
            order=order,
            book=item.book,
            title=item.book.title,
            authors=item.book.authors,
            price=item.book.price,
            quantity=item.quantity,
        )

    cart.items.all().delete()
    request.session.pop('checkout_data', None)

    return JsonResponse({
        'success': True,
        'order_id': order.pk,
        'redirect': f'/order-success/{order.pk}/',
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_success.html', {'order': order})


# ─── Wishlist ──────────────────────────────────────────────────────────────────

@require_POST
def toggle_wishlist(request, book_id):
    """Add/remove a book from the user's wishlist. Returns JSON."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'login_required'}, status=401)
    book = get_object_or_404(Book, pk=book_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, book=book)
    if not created:
        obj.delete()  # toggle off
        return JsonResponse({'success': True, 'wishlisted': False, 'message': 'Removed from wishlist'})
    return JsonResponse({'success': True, 'wishlisted': True, 'message': 'Added to wishlist ♥'})


@login_required
def wishlist_page(request):
    """Page showing all of the user's wishlisted books."""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('book', 'book__category')
    wishlist_book_ids = list(wishlist_items.values_list('book_id', flat=True))
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_book_ids': wishlist_book_ids,
    }
    return render(request, 'store/wishlist.html', context)

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items', 'items__book').order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})
