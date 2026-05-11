from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from products.models import Product
from category.models import Category
from django.core.paginator import Paginator




def home_page(request):

    categories = Category.objects.filter(is_active=True)   
    products = Product.objects.select_related('category').all().order_by('-id')[:8]

    return render(request,'home.html', {
        'categories' : categories,
        'products' : products  
    })


def user_product_list(request, category_id=None):
    products = Product.objects.all()
    categories = Category.objects.filter(is_active=True)
    
    category = None
    category_id = request.GET.get('category')

    if category_id:
        category = get_object_or_404(Category,id=category_id)
        products = products.filter(category=category)

    
    search_query = request.GET.get('search','')
    sort_option = request.GET.get('sort','')
    min_price = request.GET.get('min_price','')
    max_price = request.GET.get('max_price','')

    if search_query:
        products = products.filter(product_name__icontains=search_query)

    if min_price:
        products = products.filter(base_price__gte=min_price)

    if max_price:
        products = products.filter(base_price__lte=max_price) 

    if sort_option == 'price_low':
        products = products.order_by('base_price') 
    elif sort_option == 'price_high':
        products = products.order_by('-base_price')
    elif sort_option == 'a_z':
        products = products.order_by('product_name') 
    elif sort_option == 'z_a':
        products = products.order_by('-product_name')                     

     
    paginator = Paginator(products,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

        
    return render(request,'user_product_list.html', {
        'page_obj': page_obj,
        'category': category,
        'search_query': search_query,
        'sort_option': sort_option,
        'min_price': min_price,
        'max_price': max_price,
        'categories': categories,

    })


def user_product_details(request,pk):
    categories = Category.objects.filter(is_active=True)
    product = Product.objects.get(pk=pk)

    variants = product.variants.all()

    sizes = variants.values_list('size', flat=True).distinct()
    colors = variants.values_list('color', flat=True).distinct()
        
    related_products = Product.objects.filter(
        category = product.category,
        is_listed=True
    ).exclude(id=product.id)[:4]

    if not product.is_available or product.is_blocked or product.stock <= 0:
        messages.error(request,'Product Unavailable')
        return redirect('product_unavailable')

    return render(request,'user_product_details.html',{
        'product': product,
        'related_products': related_products,
        'categories': categories,
        'sizes': sizes,
        'colors': colors,
    })


def product_unavailable(request):

    return render(request,'product_unavailable.html')
