from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_view, name='search'),
    path('books/', views.book_list_view, name='book_list'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('book/<slug:slug>/', views.book_detail, name='book_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/json/', views.cart_json, name='cart_json'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('buy-now/<int:book_id>/', views.buy_now, name='buy_now'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    # Wishlist
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('wishlist/toggle/<int:book_id>/', views.toggle_wishlist, name='toggle_wishlist'),
]
