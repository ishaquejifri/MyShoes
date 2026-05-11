from django.shortcuts import render,redirect,get_object_or_404
import random
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate,get_user_model,login,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import CustomUser,Address
from .forms import SignupForm, LoginForm,AddressForm
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from products.models import Category



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
        
        otp = generate_otp()

        request.session['signup_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'password': password,
            'otp': otp
        }

        request.session['otp'] = otp
        request.session['signup_email'] = email
        request.session['otp_purpose'] = 'signup'

        send_mail(
            'Your OTP Code',
            f'Your OTP for signup is {otp}',
            'ishaque7jifri@gmail.com',
            [email],
            fail_silently=False,

        )
        print('otp1:',otp)
                
    
        return redirect('verify_otp')
    
    return render(request,'signup.html')

def generate_otp():
    return str(random.randint(100000, 999999))

@never_cache
def verify_otp(request):
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        signup_data = request.session.get('signup_data')

        if signup_data:
            if entered_otp == signup_data['otp']:

                user = User.objects.create_user(
                    username=signup_data['email'],
                    email=signup_data['email'],
                    first_name = signup_data['first_name'],
                    last_name = signup_data['last_name'],
                    password= signup_data['password'],
                    phone= signup_data['phone']
            )

                del request.session['signup_data']

                messages.success(request, 'Account created successfully')
                return redirect('login')
            else:
                messages.error(request, 'Invalid OTP')
                return redirect('verify_otp')

        reset_email = request.session.get('reset_email')
        reset_otp = request.session.get('reset_otp')

        if reset_email and reset_otp:
            if str(entered_otp) == str(reset_otp):
                return redirect('new_password')
            else:
                messages.error(request,'Invalid OTP')
                return redirect('verify_otp')

        messages.error(request,'Session Expired. Try again!')
        return redirect('login')       

    return render(request,'email/verify_otp.html')

@never_cache
def resend_otp(request):

    signup_data = request.session.get('signup_data')

    if not signup_data:
        return request('signup')
    
    otp = generate_otp()
    signup_data['otp'] = otp
    request.session['signup_data'] = signup_data

    send_mail(
        'Your New OTP',
        f'Your OTP is {otp}',
        'ishaque7jifri@gmail.com',
        [signup_data['email']],
        fail_silently=False,        
    )
    print('otp2:',otp)
    messages.success(request, 'OTP Resent Successfully')

    return redirect('verify_otp')


@never_cache
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
            messages.success(request,'Login successfully')

            request.session['just_logged_in'] = True
            # return redirect('home')
            return redirect('home')
        else:
            messages.error(request,'invalid email or password')  
       
    return render(request,'login.html')        

def logout_view(request):
    logout(request)
    messages.success(request,'Logged out successfully')
    return redirect('home')

def home(request):
    categories = Category.objects.filter(is_active=True)

    if request.session.pop('just_logged_in',False):
        messages.success(request,'You are logged in successfully')

    return render(request, "home.html",{
        'categories': categories,
    })     

        
    

def forget_password(request):

    if request.method == "POST":

        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)

            otp = random.randint(100000,999999)

            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            request.session['otp_purpose'] = 'reset_password'

            send_mail(
                "Password Reset OTP",
                f"Your OTP is {otp}",
                "ishaque7jifri@gmail.com",
                [email],
                fail_silently=False
            )

            print('forget.otp:',otp)
            return redirect("verify_otp")
        
        except User.DoesNotExist:
            messages.error(request,"Email not registered")

    return render(request,'password/forget_password.html')

def new_password(request):

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request,'Passwords do not match')
            return redirect('new_password')
        
        email = request.session.get('reset_email')

        if not email:
            messages.error(request,'Session Expired')
            return redirect('login')
        
        try:
            user = User.objects.get(email = email)
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            messages.error(request,'User not found')
            return redirect('login')    

        request.session.pop('reset_email',None)
        request.session.pop('reset_otp',None)
        
        messages.success(request,'Password reset Successful')
        return redirect('login')
    
    return render(request,'password/new_password.html')

@login_required(login_url='login')
@never_cache
def profile(request):

    addresses = Address.objects.filter(user=request.user)
    categories = Category.objects.filter(is_active=True)  

    if request.method == 'POST':
        image = request.FILES.get('profile_image')

        if image:
            request.user.profile_image = image
            request.user.save()
            messages.success(request,'Profile image updated') 
        else:
            messages.error(request,'Please select an image')     

        return redirect('profile')
        
    return render(request,'accounts/profile.html',{
        'addresses': addresses,
        'categories': categories,
        })

@login_required(login_url='login')
@never_cache
def edit_profile(request):

    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name',user.first_name)
        user.last_name = request.POST.get('last_name',user.last_name)
        user.email = request.POST.get('email',user.email)
        user.phone = request.POST.get('phone',user.phone)  

        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')

        user.save()
        messages.success(request,'Profile Updated successfully') 
        return redirect('profile')   

    return render(request, 'accounts/edit_profile.html', {'user': user})   

@login_required(login_url='login')
@never_cache
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_new_password')

        user = request.user

        if not user.check_password(current_password):
            messages.error(request,'Current password is incorrect')
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request,'New passwords not matching')
            return redirect('change_password')

        if current_password == new_password:
            messages.error(request,'New password cannot be same as old password')
            return redirect('change_password')     
        
        user.set_password(new_password) 
        user.save()

        messages.success(request,'Password changed successfully, Please login again')
        return redirect('login')

    return render(request, 'accounts/change_password.html')   

@login_required(login_url='login')
@never_cache
def change_email(request):

    if request.method == 'POST':
        new_mail = request.POST.get('email')

        if not new_mail:
            messages.error(request,'Email is required')
            return redirect('change_email')
        
        otp = random.randint(100000,999999)

        request.session['email_otp'] = otp
        request.session['new_email'] = new_mail

        try:
            send_mail(
                subject='Your otp for email change',
                message=f'Your otp is {otp}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[new_mail],
                fail_silently=False,
            )
            print('email otp:',otp)

            messages.success(request,'OTP send to your new email')
            return redirect('email_change_otp')
        except Exception as e:
            messages.error(request,f'Error sending email: {e}')
            return redirect('change_email')

    return render(request, 'accounts/change_email.html') 


@login_required(login_url='login')
@never_cache
def email_change_otp(request):
    if request.method == "POST":

        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('email_otp') 
        new_email = request.session.get('new_email')

        print("Entered OTP:", entered_otp)
        print("Session OTP:", session_otp)

        if not entered_otp:
            messages.error(request,'Enter OTP')
            return redirect('email_change_otp')

        if str(entered_otp) == str(session_otp):
            user = request.user
            user.email = new_email
            user.save()

            request.session.flush()

            messages.success(request,'Email updated successfully')
            return redirect('profile')
        else:
            messages.error(request,'Invalid OTP')

    return render(request,'accounts/email_change_otp.html')

@login_required(login_url='login')
@never_cache
def my_address(request):

    addresses = Address.objects.filter(user=request.user).order_by('-id')
    categories = Category.objects.filter(is_active=True)

    return render(request,'accounts/my_address.html',{'addresses': addresses, 'categories': categories})    

@login_required(login_url='login')
@never_cache
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_default:
                Address.objects.filter(user=request.user,is_default=True).update(is_default=False)

            if not Address.objects.filter(user=request.user).exists():
                address.is_default=True    

            address.save()
            messages.success(request,'Address added successfully')
            return redirect('my_address')
    else:
        form = AddressForm()
        print(form.errors)

    return render(request,'accounts/add_address.html',{'form': form})

def edit_address(request,id):
    address = get_object_or_404(Address,id=id,user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST,instance=address)
        if form.is_valid():

            if not form.has_changed():
                return redirect('my_address')
            
            address = form.save(commit=False)

            if address.is_default:
                Address.objects.filter(user = request.user).update(is_default = False)

            address.save()
            messages.success(request,'Address updated successfully')
            return redirect('my_address')    
    else:
        messages.error(request,'Failed to update address. Please check the form')
        form = AddressForm(instance=address)


    return render(request,'accounts/edit_address.html',{
        'form': form,
        'address':address
        })  
  
def delete_address(request,id):
    address = get_object_or_404(Address,id=id,user = request.user)
    address.delete()

    messages.success(request,'Address Deleted Successfully')
    return redirect('my_address')
