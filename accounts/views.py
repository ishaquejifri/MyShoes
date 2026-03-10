from django.shortcuts import render,redirect
import random
from django.contrib.auth import authenticate,get_user_model,login,logout
from django.core.mail import send_mail
from .models import CustomUser
from .forms import SignupForm, LoginForm
from django.contrib import messages

User = get_user_model()

def signup(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not first_name or not last_name or not email or not phone or not password or not confirm_password:
            messages.error(request,'Every Field Should be Filled')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request,'Password does not match')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request,'Email already registered')
            return redirect('signup')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            phone=phone
        )

        messages.success(request, "Account created successfully")
        return redirect("login")
    
    return render(request,'signup.html')


# def verify_otp(request):
    # user_id = request.session.get('user_id')
    # user = CustomUser.objects.get(id=user_id)

    # if request.method == 'POST':
    #     entered_otp = request.POST.get('otp')
    #     otp_obj = OTP.objects.filter(user=user).last()

    #     if otp_obj and not otp_obj.is_expired():
    #         if otp_obj.otp_code == entered_otp:
    #             user.is_active = True
    #             user.is_verified = True
    #             user.save()
    #             otp_obj.delete()
    #             login(request, user)
    #             return redirect('home')
    #         else:
    #             messages.error(request, "Invalid OTP")    
    #     else:
    #         messages.error(request, "OTP Expired")

    # return render(request, 'email/verify_otp.html')

# def resend_otp(request):
#     user_id = request.session.get('user_id')
#     user = CustomUser.objects.get(id=user_id)

#     otp_code = str(random.randint(100000, 999999))
#     OTP.objects.create(user=user, otp_code=otp_code)

#     send_mail(
#         'Resend OTP',
#         f'Your new OTP is {otp_code}',
#         'admin@myshoes.com',
#         [user.email],
#     )

#     return redirect('verify_otp')

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request,username=email,password=password)

        if user is not None:
            if user.is_block:
                messages.error(request,'your account is blocked by admin')
                return redirect('login')
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'invalid email or password')
    return render(request,'login.html')        

def logout_view(requset):
    logout(requset)
    return redirect('login')

def home(request):
    return render(request, "home.html")   

        
    

def forget_password(request):
    return render(request,'password/forget_password.html')

def new_password(request):
    return render(request,'password/new_password.html')

def profile(request):
    return render(request,'accounts/profile.html')

def edit_profile(request):
    return render(request, 'accounts/edit_profile.html')    