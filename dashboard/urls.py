from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Admin Routes
    path('admin/', views.admin_home, name='admin_home'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/toggle/<int:pk>/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    path('admin/sellers/', views.admin_sellers, name='admin_sellers'),
    path('admin/sellers/toggle/<int:pk>/', views.admin_toggle_seller_approval, name='admin_toggle_seller_approval'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/books/', views.admin_books, name='admin_books'),
    path('admin/books/add/', views.admin_add_book, name='admin_add_book'),
    path('admin/books/toggle/<int:book_id>/', views.admin_toggle_featured, name='admin_toggle_featured'),
    path('admin/books/delete/<int:pk>/', views.admin_delete_book, name='admin_delete_book'),
    path('admin/categories/', views.admin_categories, name='admin_categories'),

    # Seller Routes
    path('seller/', views.seller_home, name='seller_home'),
    path('seller/books/', views.seller_books, name='seller_books'),
    path('seller/books/add/', views.seller_add_book, name='seller_add_book'),
    path('seller/books/edit/<int:pk>/', views.seller_edit_book, name='seller_edit_book'),
    path('seller/books/delete/<int:pk>/', views.seller_delete_book, name='seller_delete_book'),
]
