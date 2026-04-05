from django.contrib import admin
from .models import Category, Book, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['title', 'authors', 'price', 'quantity', 'subtotal']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'category', 'price', 'stock', 'is_featured', 'is_bestseller']
    list_filter = ['category', 'is_featured', 'is_bestseller']
    search_fields = ['title', 'authors']
    list_editable = ['price', 'stock', 'is_featured', 'is_bestseller']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['google_books_id', 'created_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'user', 'item_count', 'total', 'created_at']
    readonly_fields = ['session_key', 'created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'total', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['full_name', 'email', 'razorpay_payment_id']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'created_at']
