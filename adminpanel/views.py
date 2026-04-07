from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from .decorators import admin_required
from accounts.models import CustomUser
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

User = get_user_model()


@never_cache
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
       
        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_staff:
                login(request,user)
                return redirect('admin_dashboard')
            else:
                messages.error(request,'You are not autherized to access admin panel')
        else:
            messages.error(request,'Invalid username or password')                

    return render(request, "admin_login.html")



# @admin_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# @admin_required
@never_cache
@login_required
@staff_member_required(login_url='admin_login')
def admin_dashboard(request):
    
    return render(request, "dashboard.html")

# @admin_required
def user_list(request):

    search_query = request.GET.get('search','')

    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    paginator = Paginator(users,5)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query
    }

    

    return render(request, "user_list.html", context)


def admin_sales_report(request):

    return render(request,'sales_report.html') 

def toggle_block_user(request, user_id):
    user = get_object_or_404(User,id=user_id)

    if user.is_block:
        user.is_block = False
        messages.success(request,'User unblocked successfully')
    else:
        user.is_block = True
        messages.success(request,'User blocked successfully') 

    user.save()

    return redirect('user_list')       
