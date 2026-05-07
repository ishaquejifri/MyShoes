from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,ProductImage,ProductVariant
from .forms import ProductForm, ProductVariantForm
from category.models import Category
from django.contrib.auth.decorators import login_required
import base64
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.contrib import messages

# Create your views here.

@login_required(login_url='admin_login')
@never_cache
def product_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    products = Product.objects.filter(is_deleted=False).order_by('-id')

    if query:
        products = products.filter(product_name__icontains=query)     

    if category_id:         
         products = products.filter(category_id=category_id) 

    paginator = Paginator(products,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)        

    return render(request, 'product_list.html', { 
          'products': page_obj,
          'page_obj':page_obj,
          'query': query
          })

@login_required(login_url='admin_login')
@never_cache
def add_product(request):

    form = ProductForm(request.POST or None, request.FILES or None)
    categories = Category.objects.all()

    
    files = request.FILES.getlist('gallery_images')
    cropped_gallery_images = request.POST.getlist('cropped_gallery_images')

    total_images = len(files) if files else len(cropped_gallery_images)

    if request.method == 'POST':

        if total_images < 3 :
                form = ProductForm(request.POST,request.FILES)
                messages.error(request,'Please Upload atleast 3 Images')
        elif total_images > 5:
                form = ProductForm(request.POST,request.FILES)
                messages.error(request,'Maximum 5 Images are Allowed')   
        else:
               form = ProductForm(request.POST,request.FILES)
               
               if form.is_valid():
                   product = form.save(commit=False)

                   cropped_image = request.POST.get('cropped_image')

                   if cropped_image:                    
                    format,imgstr = cropped_image.split(';base64,')
                    ext = format.split('/')[-1]

                    product.image = ContentFile(
                        base64.b64decode(imgstr),
                        name='cropped.' + ext
                    )

                    product.save()    

                    if cropped_gallery_images:
                        for img in cropped_gallery_images:
                             format, imgstr = img.split(';base64,')
                             ext = format.split('/')[-1]

                             file = ContentFile(
                               base64.b64decode(imgstr),
                               name='gallery.' + ext
                            )

                             ProductImage.objects.create(product=product, image=file)

                    else:
                        for file in files:
                            ProductImage.objects.create(product=product, image=file)
                            
            
                    messages.success(request,'Product Added Successfully!')
                    return redirect('product_list')
               else:
                    messages.error(request,'Please correct the form Errors')                           
    
    return render(request,'add_product.html',{
        'form': form,
        'categories': categories  
          })

@login_required(login_url='admin_login')
@never_cache
def edit_product(request,id):
    product = get_object_or_404(Product,id=id)
    gallery_images = product.images.all()

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            updated_product = form.save(commit=False)

            updated_product.is_blocked = product.is_blocked
            updated_product.is_listed = product.is_listed
            updated_product.is_available = product.is_available
            updated_product.is_deleted = product.is_deleted

            updated_product.save()

            gallery_images = request.FILES.getlist('gallery_images')

            if gallery_images:
                 updated_product.images.all().delete()

                 for image in gallery_images:
                    ProductImage.objects.create(
                      product=updated_product,
                      image = image

                 )

            return redirect('products:product_list')
        
    else:
        form = ProductForm(instance=product)
    
    return render(request,'edit_product.html',{ 
        'form': form,
        'product': product,
        'gallery_images': gallery_images,
        'categories': Category.objects.all()
          })

@login_required(login_url='admin_login')
@never_cache
def product_details(request,id):

    product = get_object_or_404(Product,id=id)
    variants = product.variants.all()


    return render(request,'product_details.html', { 
         'product': product,
         'variants': variants
                                                    })

@never_cache
@login_required(login_url='admin_login')
def add_variant(request,product_id):
     
     product = get_object_or_404(Product,id=product_id)

     if request.method=="POST":
          form = ProductVariantForm(request.POST)

          if form.is_valid():
               variant = form.save(commit=False)
               variant.product = product
               variant.save()
               return redirect('products:product_details', id=product_id)
          
     else:
          form = ProductVariantForm()

     return render(request,'add_variant.html',{
          'form': form,
          'product': product
     })


@never_cache
@login_required(login_url='admin_login')
def edit_variant(request, variant_id):
     variant = get_object_or_404(ProductVariant, id=variant_id)

     if request.method == "POST":
          form = ProductVariantForm(request.POST, instance=variant)

          if form.is_valid():
               form.save()
               return redirect('products:product_details', id=variant.product.id)
     else:
          form = ProductVariantForm(instance=variant)

     return render(request,'edit_variant.html',{
        'form': form,
        'variant': variant
     })          


def delete_variant(request, variant_id):
     variant = get_object_or_404(ProductVariant,id=variant_id)
     product_id = variant.product.id

     variant.delete()

     return redirect('products:product_details',id=product_id)

@login_required(login_url='admin_login')
@never_cache
def delete_product(request,id):
     product = get_object_or_404(Product, id=id, is_deleted=False)
     product.is_deleted = True
     product.save()
     return redirect('products:product_list')






     






