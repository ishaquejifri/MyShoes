from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .decorators import admin_required
from accounts.models import CustomUser
from django.core.paginator import Paginator
from django.db.models import Q

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "adminpanel/admin_login.html")

# def admin_login(request):
#     return render(request,'adminpanel/dashboard.html')

@admin_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@admin_required
def admin_dashboard(request):
    total_users = CustomUser.objects.filter(is_staff=False).count()
    blocked_users = CustomUser.objects.filter(is_blocked=True).count()

    context = {
        'total_users': total_users,
        'blocked_users': blocked_users
    }

    return render(request, "adminpanel/dashboard.html", context)

@admin_required
def user_list(request):

    search_query = request.GET.get('search', '')

    users = CustomUser.objects.filter(is_staff=False)

    # SEARCH
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # SORT LATEST FIRST
    users = users.order_by('-created_at')

    # PAGINATION
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    context = {
        'users': users_page,
        'search_query': search_query
    }

    return render(request, "adminpanel/user_list.html", context)

@admin_required
def toggle_block_user(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    if user.is_blocked:
        user.is_blocked = False
    else:
        user.is_blocked = True

    user.save()

    return redirect('user_list')