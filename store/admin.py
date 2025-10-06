from django.contrib import admin
from .models import Category, MenuItem, Cart, CartItem, Order, OrderItem

# ----------------------
# Category Admin
# ----------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# ----------------------
# MenuItem Admin
# ----------------------
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'gst_rate', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')
    list_editable = ('price', 'is_active')

# ----------------------
# Cart Admin
# ----------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key')
    search_fields = ('user__username', 'session_key')

# ----------------------
# CartItem Admin
# ----------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user__username', 'product__name')

# ----------------------
# Order Admin
# ----------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'total_amount', 'payment_status', 'status')
    list_filter = ('payment_status', 'status')
    search_fields = ('user__username', 'full_name', 'status')

# ----------------------
# OrderItem Admin
# ----------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'gst_rate')
    search_fields = ('order__id', 'product__name')






