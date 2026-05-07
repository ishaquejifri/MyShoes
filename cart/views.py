from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart,CartItem
from django.http import JsonResponse
from django.contrib import messages
from category.models import Category


# Create your views here.


def add_to_cart(request,product_id):
    if not request.user.is_authenticated:
        messages.warning(request,"⚠️ Please Login to purchase the Product")
        return redirect(f'/user/login/?next=/cart/add/{id}/')

    product = get_object_or_404(Product,id=product_id)

    
    if product.stock <= 0 or not product.is_available or product.is_blocked:
        messages.error(request, "This product is unavailable.")
        return redirect('user_product_list')

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': 1,
            'price': product.base_price
                  })

    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Quantity increased in cart.")
    else:
        messages.error(request, "No more stock available.")

    return redirect('cart:view_cart') 

@login_required
def view_cart(request):
    categories = Category.objects.filter(is_active=True)
    cart, created = Cart.objects.get_or_create(user = request.user)
    cart_items = cart.items.all()

    cart_count = sum(item.quantity for item in cart.items.all())
    total = sum(item.subtotal() for item in cart_items)

    return render(request,'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'cart_count': cart_count,
        'categories': categories,
    })  

@login_required
def update_cart(request,item_id, action):
    cart_item = get_object_or_404(CartItem,id=item_id,cart__user=request.user)

    if action == 'increase' and cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1

    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return redirect('cart:view_cart')

    cart_item.save()
    return redirect('cart:view_cart')  

@login_required
def ajax_update_cart(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')

        cart_item = get_object_or_404(CartItem,id=item_id,cart__user=request.user)

        if action == 'increase':
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
        cart_item.save()

        cart = cart_item.cart
        total = sum(item.subtotal() for item in cart_item.cart.items.all())

        return JsonResponse({
            'quantity': cart_item.quantity,
            'subtotal': cart_item.subtotal(),
            'total': total,
            'cart_count': cart_item.cart.items.count()
        })                


@login_required
def remove_from_cart(request,item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()

    return redirect('cart:view_cart')
                    




