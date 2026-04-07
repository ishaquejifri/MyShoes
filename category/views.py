from django.shortcuts import render,redirect,get_object_or_404
from .models import Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator

# Create your views here.

@login_required(login_url='admin_login')
def category_list(request):
    query = request.GET.get('q')

    categories = Category.objects.all().order_by('-id')

    # categories = Category.objects.annotate(
    #     product_count=Count('product')
    # )

    if query:
        categories = categories.filter(name__icontains=query)

    paginator = Paginator(categories,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    

    return render(request,'category_list.html',{
        'page_obj': page_obj,
        'query': query
    }) 


@login_required(login_url='admin_login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request,'Category is already exists')
            return redirect('add_category') 

        Category.objects.create(
            name = name,
            description = description,
            image = image
        ) 

        messages.success(request,'Category is successfully added')
        return redirect('category_list')  

    return render(request, 'add_category.html')


@login_required(login_url='admin_login')
def edit_category(request,id):
    category = Category.objects.get(id=id)

    if request.FILES.get('image'):
        category.image = request.FILES.get('image')

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.save()

        messages.success(request,'Category Updated Successfully')
        return redirect('category_list')
    
    return render(request,'edit_category.html',{
        'category': category
    })


@login_required(login_url='admin_login')
def toggle_category_status(request,id):
    category = Category.objects.get(id=id)
    category.is_active = not category.is_active
    category.save()

    return redirect('category_list')


@login_required(login_url='admin_login')
def delete_category(request,id):
    category = Category.objects.get(id=id)

    category.is_active = False
    category.save()

    messages.success(request,'Category is Disabled')
    return redirect('category_list')
