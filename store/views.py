from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import MenuItem, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
from .utils import get_or_create_cart, generate_gst_invoice
from django.conf import settings
import razorpay
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt



def home(request):
    items = MenuItem.objects.filter(is_active=True)
    return render(request, 'store/home.html', {'items': items})

# Correct add_to_cart view
def add_to_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(MenuItem, id=item_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

from decimal import Decimal

def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')

    total = Decimal('0.00')
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    gst_rate = Decimal('0.18')  # 18% GST as Decimal
    gst_amount = total * gst_rate
    grand_total = total + gst_amount

    context = {
        'cart_items': cart_items,
        'total': total,
        'gst_amount': gst_amount,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm

def checkout(request):
    # Get the cart for the current user/session
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get all cart items (use the correct FK 'product')
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect("home")
    
    # Compute totals using Decimal to avoid float issues
    subtotal = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
    gst_amount = sum((Decimal(item.product.price) * item.quantity * Decimal(item.product.gst_rate)) / 100 for item in cart_items)
    total_amount = subtotal + gst_amount
    
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.subtotal = subtotal
            order.gst_amount = gst_amount
            order.total_amount = total_amount
            order.payment_status = True  # mark as paid
            order.save()
            
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    # menu_item=item.product,  # use 'product' here too
                    quantity=item.quantity,
                    price=item.product.price,
                    gst_rate=item.product.gst_rate
                )
            
            # Clear cart
            cart_items.delete()
            
            return redirect("order_success", order_id=order.id)
    else:
        form = CheckoutForm()
    
    context = {
        "form": form,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "gst_amount": gst_amount,
        "total": total_amount
    }
    return render(request, "store/checkout.html", context)





def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, "store/order_success.html", {"order": order})


from django.shortcuts import render, get_object_or_404
from .models import Order, OrderItem

def download_invoice(request, order_id):
    # Get the order or 404
    order = get_object_or_404(Order, id=order_id)
    
    # Get all order items and calculate subtotal for each
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        item.subtotal = item.price * item.quantity  # Add subtotal attribute

    context = {
        "order": order,
        "order_items": order_items,
        "total": sum(item.subtotal for item in order_items)  # Optional: total sum
    }
    
    return render(request, "store/invoice.html", context)



def menu_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    return render(request, "store/menu_detail.html", {"item": item})

from django.http import JsonResponse
from .models import Cart, CartItem, MenuItem

def update_cart(request, item_id):
    cart = get_or_create_cart(request)  # Make sure you have this helper
    cart_item = CartItem.objects.filter(cart=cart, menu_item_id=item_id).first()
    
    if cart_item:
        action = request.GET.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            cart_item.quantity -= 1
        elif action == 'remove':
            cart_item.delete()
            return JsonResponse({"success": True})
        
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
    
    return JsonResponse({"success": True})

def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)  # Make sure you have this helper function
    cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=item_id)
    cart_item.delete()
    return redirect('cart')


from django.shortcuts import render, get_object_or_404
from .models import Order

def payment_success(request):
    order_id = request.session.get("order_id")
    if not order_id:
        return render(request, "store/order_success.html", {"error": "No order found."})

    order = get_object_or_404(Order, id=order_id)
    order.payment_status = "Paid"
    order.save()

    return render(request, "store/order_success.html", {"order": order})


from django.shortcuts import render
from .models import Order
from django.contrib.auth.decorators import login_required

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "store/my_orders.html", {"orders": orders})

# Correct add_to_cart view
def add_to_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(MenuItem, id=item_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

from django.shortcuts import get_object_or_404, redirect
from .models import CartItem

def increment_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.quantity += 1
    item.save()
    return redirect('cart')

def decrement_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return redirect('cart')

def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')

