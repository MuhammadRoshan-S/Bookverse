from store.models import Cart, Wishlist
from accounts.models import UserProfile


def cart_count(request):
    """Inject cart item count + wishlist count + user profile into every template context."""
    try:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        if request.user.is_authenticated:
            # Prefer user-linked cart
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                cart = Cart.objects.filter(session_key=session_key).first()
        else:
            cart = Cart.objects.filter(session_key=session_key).first()

        count = cart.item_count if cart else 0
    except Exception:
        count = 0

    # Wishlist count
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
        except Exception:
            pass

    # User profile (avatar)
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
        except Exception:
            try:
                user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
            except Exception:
                pass

    return {
        'cart_item_count': count,
        'wishlist_count': wishlist_count,
        'user_profile': user_profile,
    }
