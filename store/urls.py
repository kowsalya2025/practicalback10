from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page / Menu
    path('menu/<int:item_id>/', views.menu_detail, name='menu_detail'),  # Menu item details
    path('cart/', views.cart_view, name='cart'),  # Add this line
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart, name='update_cart'),  # Ajax update cart
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Remove item
      path('cart/increment/<int:item_id>/', views.increment_cart_item, name='increment_cart_item'),
    path('cart/decrement/<int:item_id>/', views.decrement_cart_item, name='decrement_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('payment-success/', views.payment_success, name='payment_success'),  # Direct success page
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),  # Order success
    path('download-invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),  # Invoice download

    path('my-orders/', views.my_orders, name='my_orders'),  # User order history
]
