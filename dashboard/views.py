from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, F
from store.models import Book, Order, OrderItem, Category
from accounts.models import UserProfile

def is_admin(user):
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')

def is_seller(user):
    return hasattr(user, 'profile') and user.profile.role == 'seller'

# ================================
# ADMIN DASHBOARD
# ================================
@login_required
@user_passes_test(is_admin, login_url='/')
def admin_home(request):
    total_users = User.objects.count()
    total_sellers = User.objects.filter(profile__role='seller').count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.exclude(status='cancelled').aggregate(Sum('total'))['total__sum'] or 0
    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    return render(request, 'dashboard/admin_home.html', {
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    })

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_users(request):
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'dashboard/admin_users.html', {'users': users})

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_orders.html', {'orders': orders})

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_books(request):
    books = Book.objects.select_related('seller', 'category').all().order_by('-created_at')
    return render(request, 'dashboard/admin_books.html', {'books': books})

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_toggle_featured(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    book.is_featured = not book.is_featured
    book.save()
    messages.success(request, f"Book {'featured' if book.is_featured else 'unfeatured'} successfully.")
    return redirect('dashboard:admin_books')

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_categories(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, 'Category created.')
        return redirect('dashboard:admin_categories')
    return render(request, 'dashboard/admin_categories.html', {'categories': categories})

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_sellers(request):
    sellers = User.objects.filter(profile__role='seller').order_by('-date_joined')
    return render(request, 'dashboard/admin_sellers.html', {'sellers': sellers})

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_toggle_seller_approval(request, pk):
    seller = get_object_or_404(User, pk=pk, profile__role='seller')
    seller.profile.is_approved = not seller.profile.is_approved
    seller.profile.save()
    messages.success(request, f"Seller {seller.username} {'approved' if seller.profile.is_approved else 'unapproved'}.")
    return redirect('dashboard:admin_sellers')

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_toggle_user_status(request, pk):
    user = get_object_or_404(User, pk=pk)
    if not user.is_superuser:
        user.is_active = not user.is_active
        user.save()
        messages.success(request, f"User {user.username} {'unblocked' if user.is_active else 'blocked'}.")
    return redirect('dashboard:admin_users')

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, f"Book '{book.title}' deleted successfully.")
    return redirect('dashboard:admin_books')

@login_required
@user_passes_test(is_admin, login_url='/')
def admin_add_book(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        cover_image = request.FILES.get('cover_image')
        pdf_file = request.FILES.get('pdf_file')

        category = Category.objects.filter(pk=category_id).first() if category_id else None

        book = Book.objects.create(
            title=title,
            authors=authors,
            description=description,
            category=category,
            price=price,
            cover_image=cover_image,
            pdf_file=pdf_file,
            seller=None  # published directly by admin
        )
        messages.success(request, 'Book published successfully!')
        return redirect('dashboard:admin_books')

    return render(request, 'dashboard/seller_form.html', {'categories': categories})

# ================================
# SELLER DASHBOARD
# ================================
@login_required
@user_passes_test(is_seller, login_url='/')
def seller_home(request):
    items = OrderItem.objects.filter(book__seller=request.user, order__status='paid')
    total_purchases = items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_earnings = items.annotate(sub=F('price') * F('quantity')).aggregate(total=Sum('sub'))['total'] or 0
    total_books = Book.objects.filter(seller=request.user).count()

    return render(request, 'dashboard/seller_home.html', {
        'total_purchases': total_purchases,
        'total_earnings': total_earnings,
        'total_books': total_books,
    })

@login_required
@user_passes_test(is_seller, login_url='/')
def seller_books(request):
    books = Book.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'dashboard/seller_books.html', {'books': books})

@login_required
@user_passes_test(is_seller, login_url='/')
def seller_add_book(request):
    # Enforce approval status
    if not request.user.profile.is_approved:
        messages.error(request, 'Your seller account is under review. You cannot add books yet.')
        return redirect('dashboard:seller_home')

    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        price = request.POST.get('price')
        cover_image = request.FILES.get('cover_image')
        pdf_file = request.FILES.get('pdf_file')

        category = Category.objects.filter(pk=category_id).first() if category_id else None

        book = Book.objects.create(
            title=title,
            authors=authors,
            description=description,
            category=category,
            price=price,
            cover_image=cover_image,
            pdf_file=pdf_file,
            seller=request.user
        )
        messages.success(request, 'Book uploaded successfully!')
        return redirect('dashboard:seller_books')

    return render(request, 'dashboard/seller_form.html', {'categories': categories})

@login_required
@user_passes_test(is_seller, login_url='/')
def seller_edit_book(request, pk):
    # Enforce approval status
    if not request.user.profile.is_approved:
        messages.error(request, 'Your seller account is under review. You cannot edit books.')
        return redirect('dashboard:seller_home')

    book = get_object_or_404(Book, pk=pk, seller=request.user)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.authors = request.POST.get('authors')
        book.description = request.POST.get('description', '')
        cat_id = request.POST.get('category')
        book.category = Category.objects.filter(pk=cat_id).first() if cat_id else None
        book.price = request.POST.get('price')
        
        if request.FILES.get('cover_image'):
            book.cover_image = request.FILES.get('cover_image')
        if request.FILES.get('pdf_file'):
            book.pdf_file = request.FILES.get('pdf_file')
            
        book.save()
        messages.success(request, 'Book updated successfully!')
        return redirect('dashboard:seller_books')

    return render(request, 'dashboard/seller_form.html', {'book': book, 'categories': categories})

@login_required
@user_passes_test(is_seller, login_url='/')
def seller_delete_book(request, pk):
    # Enforce approval status
    if not request.user.profile.is_approved:
        messages.error(request, 'Your seller account is under review. You cannot delete books.')
        return redirect('dashboard:seller_home')

    book = get_object_or_404(Book, pk=pk, seller=request.user)
    book.delete()
    messages.success(request, 'Book deleted.')
    return redirect('dashboard:seller_books')

