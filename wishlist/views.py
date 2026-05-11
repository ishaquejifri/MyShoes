from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Wishlist
from products.models import Product
from category.models import Category
from decimal import Decimal

# Create your views here.

def wishlist(request):
    categories = Category.objects.filter(is_active=True)

    if not request.user.is_authenticated:
        return redirect('login')
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')

    total_price = sum(
        (
            item.product.offer_price or item.product.base_price or Decimal('0.00')
        )
           for item in wishlist_items
    )

    context = {
        'wishlist_items': wishlist_items,
        'total_price': total_price,
        'categories': categories,
    }

    return render(request,'wishlist.html', context)


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request,'Please Login First')
        return redirect('login')
    
    product = get_object_or_404(Product, id=product_id)

    wishlist_item,created = Wishlist.objects.get_or_create(user = request.user,product=product)

    if created:
        messages.success(request,'Product Added to the Wishlist')
    else:
        messages.info(request,'Product Already in Wishlist')

    return redirect(request.META.get('HTTP_REFERER'))  


def remove_wishlist(request,wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id,user=request.user)
    wishlist_item.delete()

    messages.success(request,'Item Removed from Wishlist')

    return redirect('wishlist')

