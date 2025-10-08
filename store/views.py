from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import MenuItem, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm

# ---------------- Helper: get or create cart ---------------- #
def get_or_create_cart(request):
    if request.user.is_authenticated and not request.user.is_anonymous:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    # Guest cart via session
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.filter(id=cart_id).first()
        if cart:
            return cart
    cart = Cart.objects.create()
    request.session['cart_id'] = cart.id
    return cart

# ---------------- Home ---------------- #
def home(request):
    items = MenuItem.objects.filter(is_active=True)
    return render(request, 'store/home.html', {'items': items})

# ---------------- Menu Detail ---------------- #
def menu_detail(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    return render(request, 'store/menu_detail.html', {'item': item})

# ---------------- Cart Views ---------------- #
def add_to_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(MenuItem, id=item_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    total = sum(item.product.price * item.quantity for item in cart_items)
    gst_rate = Decimal('0.18')
    gst_amount = total * gst_rate
    grand_total = total + gst_amount

    context = {
        'cart_items': cart_items,
        'total': total,
        'gst_amount': gst_amount,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)

def update_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = CartItem.objects.filter(cart=cart, product_id=item_id).first()
    if cart_item:
        action = request.GET.get('action')
        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()
        elif action == 'remove':
            cart_item.delete()
    return JsonResponse({"success": True})

def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=item_id)
    cart_item.delete()
    return redirect('cart')

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

# ---------------- Checkout ---------------- #
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('product')
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('home')

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    gst_amount = sum((item.product.price * item.quantity * item.product.gst_rate / 100) for item in cart_items)
    total_amount = subtotal + gst_amount

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.subtotal = subtotal
            order.gst_amount = gst_amount
            order.total_amount = total_amount
            order.payment_status = True
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    gst_rate=item.product.gst_rate
                )

            cart_items.delete()
            return redirect('order_success', order_id=order.id)
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'gst_amount': gst_amount,
        'total': total_amount
    }
    return render(request, 'store/checkout.html', context)

# ---------------- Order Success ---------------- #
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})

# ---------------- Download Invoice ---------------- #
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Compute subtotal dynamically
    items_with_subtotal = []
    for item in order_items:
        items_with_subtotal.append({
            'item': item,
            'subtotal': item.price * item.quantity
        })

    total = sum(i['subtotal'] for i in items_with_subtotal)

    context = {
        'order': order,
        'order_items': items_with_subtotal,
        'total': total
    }

    return render(request, 'store/invoice.html', context)


# ---------------- Payment Success ---------------- #
def payment_success(request):
    order_id = request.session.get('order_id')
    if not order_id:
        return render(request, 'store/order_success.html', {"error": "No order found."})
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = True
    order.save()
    return render(request, 'store/order_success.html', {"order": order})

# ---------------- My Orders ---------------- #
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/my_orders.html', {'orders': orders})

