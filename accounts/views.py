import random
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate ,login,logout
from accounts.models import Profile
from accounts.models import Address
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from cart.models import Order,CartItem,Cart
from product.models import Wishlist
from django.db.models import Q
from django.db.models import Count






def login_page(request):
    if request.method =='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        profile_obj=Profile.objects.filter(username=email)


        if not profile_obj.exists():
            messages.warning(request,'Account not found!')
            return HttpResponseRedirect(request.path_info)

        if not profile_obj[0].is_email_verified:
            messages.warning(request, 'Your Account need to be verified!')
            return HttpResponseRedirect(request.path_info)

        profile_obj = authenticate(username = email,password=password)
        if profile_obj:
            login(request,profile_obj)
            return redirect('/')

        messages.success(request, 'Invalid Credentials!')
        return HttpResponseRedirect(request.path_info)


    return render(request, "login2.html")

def register_page(request):
    if request.method =='POST':
        try:
            get_otp = request.POST.get('otp')
        except:
            get_otp = None
        if get_otp:
            email = request.POST.get('email')
            profile_obj =Profile.objects.get(username=email)
            if profile_obj.email_token == get_otp:
                profile_obj.is_email_verified = True
                profile_obj.save()
                return redirect("login_page")
            context = {
                "otp": True,
                "message": messages.warning(request, "Invalid OTP"),
                "email": email,
            }
            return render(request, "register1.html",context)



        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')
        phone_number = request.POST.get('phone_number')

        profile_obj = Profile.objects.filter(username=email)



        if password != re_password:
            messages.warning(request, 'The passwords do not match.')
            return HttpResponseRedirect(request.path_info)

        if profile_obj.exists():
            messages.warning(request,'Email already exist')
            return HttpResponseRedirect(request.path_info)


        profile_obj= Profile.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            username = email
        )
        profile_obj.set_password(password)
        email_token = random.randint(100000,999999)
        profile_obj.email_token = email_token
        profile_obj.save()
        subject='your account need to be verified'
        email_from = settings.EMAIL_HOST_USER
        message = f'hi please enter the below code to complete verification : {email_token}'
        send_mail(subject,message,email_from,[email])
        messages.success(request, 'An otp has been sent on your mail.')
        return render(request, 'register1.html',{'otp':True,'email':email} )




    return render(request,'register1.html')

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart




def user_logout(request):
    logout(request)
    return redirect('/')  

def user_profile(request):
    counter = 0
    total_orders = Order.objects.filter(status = 'Order placed').aggregate(total_orders=Count('uid'))['total_orders']
    cart,_=Cart.objects.get_or_create(cart_id=_cart_id(request))
    cart_items=CartItem.objects.filter(cart=cart,active=True)
    for cart_item in cart_items:
            counter += 1
    
    recent_orders = Order.objects.filter(Q(user=request.user),~Q(status ='Order Pending')).order_by('-created_at')[:2]
    total_wishlist= Wishlist.objects.filter(user=request.user).aggregate(total_wishlist=Count('uid'))['total_wishlist']
    
    return render(request,'user-profile.html',{'total_orders':total_orders,'counter':counter,'recent_orders':recent_orders,'total_wishlist':total_wishlist} )
    

def address_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request,'address.html',{'address':addresses})


def add_address(request):
    if request.method =='POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        house_name = request.POST.get('house_name')
        street = request.POST.get('road_name')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        city = request.POST.get('city')
        phone_number = request.POST.get('phone_number')
        alternate_number = request.POST.get('alternate_number')
        
        address = Address.objects.create( user=request.user,first_name=first_name,last_name=last_name,house_name=house_name,street=street,pincode=pincode,state=state,city=city,phone_number=phone_number,alternate_number=alternate_number)
        address.save()
        
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
def edit_address(request,ad_id):
    if request.method =='POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        house_name = request.POST.get('house_name')
        street = request.POST.get('road_name')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        city = request.POST.get('city')
        phone_number = request.POST.get('phone_number')
        alternate_number = request.POST.get('alternate_number')
        
        
        address = Address.objects.get(uid=ad_id)
        address.first_name = first_name
        address.last_name=last_name
        address.house_name=house_name
        address.road_name=street
        address.pincode=pincode
        address.state=state
        address.city=city
        address.phone_number=phone_number
        address.alternate_number=alternate_number
        
        address.save()
    return redirect('user_address')

def delete_address(request,add_id):
    
    address = Address.objects.get(uid=add_id)
    address.delete()
    return redirect('user_address')


def user_detail(request):
    
    return render(request, 'user-details.html')


def edit_user_detail(request,user_id):
    if request.method =='POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        
        users = Profile.objects.get(id=user_id)
        users.first_name=first_name
        users.last_name=last_name
        users.phone_number=phone_number
        
        users.save()
    return redirect('user_detail')


def change_profile_picture(request,user_id):
    if request.method == 'POST':
        profile_image = request.FILES.get('profile_image')
        images = Profile.objects.get(id=user_id)
        
        images.profile_image=profile_image
        
        images.save()
    
        
    return redirect('user_detail')
    
# change password template    
def ResetPassword(request):
    
    return render(request,'change-password.html')   


def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_password')

        print(old_password,'---------------')

        # Validation
        if new_password != confirm_new_password:
            messages.error(request, 'Password did not match')
            return redirect('change_password')

        user = request.user  # The authenticated user

        if check_password(old_password, user.password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully')
            return redirect('login_page')
        else:
            messages.error(request, 'Invalid old password')
            return redirect('change_password')

    return render(request, 'change-password.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user_profile = Profile.objects.get(username=email)
        except Profile.DoesNotExist:
            messages.warning(request, 'Account not found!')
            return redirect('forgotPassword')

        # Generate and save a password reset token
        password_reset_token = 'generate_your_password_reset_token_here'
        user_profile.password_reset_token = password_reset_token
        user_profile.save()

        
        request.session['password_reset_email'] = email

        # Redirect to the password reset form
        return redirect('resetPassword')

    return render(request, 'forgot-password.html')

# password reset for forgott password
def reset_password(request):
    if 'password_reset_email' not in request.session:
        messages.warning(request, 'Invalid request. Please start the password reset process again.')
        return redirect('forgotPassword')

    if request.method == 'POST':
        email = request.session['password_reset_email']
        user_profile = Profile.objects.get(username=email)

        new_password = request.POST.get('new_password')
        user_profile.set_password(new_password)
        user_profile.save()

        del request.session['password_reset_email']

        return redirect('login_page')

    return render(request, 'reset-password.html')


@login_required
def user_orders(request):
    orders = Order.objects.filter(Q(user= request.user),~Q(status = 'Order Pending'))
    return render(request,'user-order-details.html',{'orders':orders})

def user_single_order(request,order_id):

    try:
        order = Order.objects.get(uid=order_id)
        order_items = order.order_item.all()
        return render(request, 'user-single-order-details.html', {'order': order, 'order_items': order_items})
    except Order.DoesNotExist:
        pass
    

def cancel_order(request,order_id):
    order = Order.objects.get(uid = order_id)
    if order.status == 'Cancelled':
       messages.info(request, 'This order is already cancelled.')
        
    else:
        order.status = 'Cancelled'
        order.save()
        
        messages.success(request, 'Your order has been successfully cancelled.')
        
        
    return redirect('userOrders')

def return_order(request,order_id):
    order = Order.objects.get(uid= order_id)
    if order.status != 'Delivered':
        messages.error(request, 'This order cannot be returned.')
        
    else:
        order.status = 'Returned'
        order.save()
        
        messages.success(request, 'Your order has been returned successfully.')
        
    return redirect('userOrders')

