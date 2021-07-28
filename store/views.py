from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login as auth_login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from twilio.rest import Client
import random

from django.core.files.base import ContentFile #base 64 to image conversion
import base64

from django.http import HttpResponseRedirect  #for   META['HTTP_REFERER']

import json
from django.http import JsonResponse

import uuid  #uuid referral

from django.contrib import messages,auth

from cart.views import _cart_id
from cart.models import Cart,CartItem

from product.models import Product,ProductOffer
from category.models import Category,CategoryOffer
from accounts.models import Account,UserPropic,UserAddress
from orders.models import *
from referral.models import Referral, ReferralUsers,ReferralControl,ReferralCoupon

import requests
from .forms import AccountForm

# Create your views here.
def home(request):
    obj = Product.objects.all().filter(is_available = True)
    obj2 = Category.objects.all()
    context = {
        'products' : obj,
        'categories' : obj2
    }
    return render(request,'store/home.html',context)


def signup(request):
   
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(first_name,last_name,phone_number,email,password,"====================signup")
        username = email.split('@')[0]



        # cpassword=request.POST.get('confirm_password')
        # print(username)
        # if cpassword != password:
        #     print("password mismatch")
        #     messages.info(request, 'password mismatch')
        #     return redirect('signup')
        # if len(phone_number) != 10 :
        #     messages.info(request, 'Enter a valid Phone number')
        #     return redirect('signup')
            # context = {
            # 'form': form
            # }
            # return render(request,'accounts/signup.html')
        if Account.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({'status':False,'message':"phone number already exists"})

            # messages.info(request, 'phone number already exists')
            # print("phone")
            # return redirect('signup')

        if Account.objects.filter(email=email).exists() :
            return JsonResponse({'status':False,'message':"email already exists"})

            # messages.info(request, 'email already exists')
            # print("email")
            # return redirect('signup')


        # form = AccountForm(request.POST)
        # if form.is_valid():
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # phone_number = form.cleaned_data['phone_number']
            # email = form.cleaned_data['email']
            # password = form.cleaned_data['password']
            # username = email.split('@')[0]
        if Account.objects.filter(phone_number=phone_number).exists() != True and Account.objects.filter(email=email).exists() != True :
            print("save",username)
            user = Account.objects.create_user(first_name = first_name, last_name = last_name, phone_number = phone_number,email = email,password = password,username = username)
            user.save()
            
            if request.session.get('ref_code'):
                referral_code = request.session.get('ref_code')
                print(referral_code,"referral code session=======")

                if ReferralUsers.objects.filter(referral_code = referral_code).exists(): #check referral user exists
                    print("============================session referral exists")

                    referred_user_instance = ReferralUsers.objects.get(referral_code = referral_code) #get user referral instance
                    control_instance = ReferralControl.objects.first()
                    

                    try:
                        if control_instance.is_available != True : #cannot add referral when referral control is false
                            return JsonResponse({'status':True,'message':"You are registered!!!!  referral unavailable "})  
                    except:  #when is_available is not added
                        return JsonResponse({'status':True,'message':"You are registered!!!!  referral unavailable "})  

                    if control_instance.check_expired_date_only == True: #cannot  add referral when expired in date and available
                        return JsonResponse({'status':True,'message':"You are registered!!!!  referral expired "})  


                    print("==referral limit exceeded before if=====",referred_user_instance.referral_count,"not < ",control_instance.referral_user_limit)
                    if int(referred_user_instance.referral_count) < int(control_instance.referral_user_limit) :#add only when referral count less than referral limit

                        print("=====================create referral")

                        new_referral_instance = Referral()
                        new_referral_instance.user = user
                        new_referral_instance.recommended_user = referred_user_instance.user
                        new_referral_instance.referral_code = referral_code
                        new_referral_instance.save()   #referral table added

                        add_coupon_signup_user = ReferralCoupon()
                        add_coupon_signup_user.user = user
                        add_coupon_signup_user.discount_amount = control_instance.referral_amount
                        add_coupon_signup_user.referral_end = control_instance.referral_end_date
                        add_coupon_signup_user.save()

                        add_coupon_recommended_user = ReferralCoupon()
                        add_coupon_recommended_user.user = referred_user_instance.user
                        add_coupon_recommended_user.discount_amount = control_instance.referral_amount
                        add_coupon_recommended_user.referral_end = control_instance.referral_end_date
                        add_coupon_recommended_user.save()

                        referred_user_instance.referral_count =int(referred_user_instance.referral_count) + 1
                        referred_user_instance.save() 

                        return JsonResponse({'status':True,'message':"You are registered!!!! with referral "})     

                    else:
                        del request.session['ref_code']
                        return JsonResponse({'status':True,'message':"You are registered!!!!referral limit exceeded"})     
                else:
                    if request.session.get('ref_code'):
                        del request.session['ref_code']
                    return JsonResponse({'status':True,'message':"You are registered!!!! but invalid referral"})

            return JsonResponse({'status':True,'message':"You are registered!!!!"})
          

            # messages.info(request, 'You are registered')

    # else:
    #     form = AccountForm()

    # context = {
    #     'form': form
    # }
    return render(request,'accounts/register.html')

#===========================referral session creation end
def signout(request):
    logout(request)
    return redirect('/') 

def login(request):
    if  request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = email.split('@')[0]

        user = authenticate(username=username,password=password)
        print("----------------------------------------------------------------",user)
        if Account.objects.filter(email=email).exists() :
            obj = Account.objects.get(email=email)
            print(" in if")
            if obj.is_active != True:
                print("check true active")
                return JsonResponse({'status':False,'message':"Your account has been blocked"})

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass
            
            auth_login(request,user)
            # return redirect('home')
            return JsonResponse({'status':True,'message':"Login successful"})

        else:
            return JsonResponse({'status':False,'message':"Invalid username or password"})

    return render(request,'accounts/login.html')
#---------------------------------------------------------------------------OTP LOGIN------------------

def login_otp(request):
    if request.method=='POST':
        phone=request.POST['phone_number']
        if Account.objects.filter(phone_number=phone).exists():
            otp = random.randint(100000,999999)
            strotp=str(otp)
            account_sid ='ACca48f33a1a36f7da7d530b7397521bde'
            auth_token ='34bfdcb6e74a3ba13c230ab16935daa6'
            client = Client(account_sid, auth_token)

            message = client.messages \
                .create(
                     body="Your Cheq login OTP is "+strotp,
                     from_='+16105699980',
                     to='+91'+phone
                 )
            request.session['otp']=otp
            print(request.session['otp'])
            request.session['phone']=phone
            print(request.session['phone'])
            print(otp,phone)
            messages.success(request,"OTP Sended Successfully")
            return redirect('login_otp')  
        messages.error(request,"enter valid phone number")    
        return redirect('login_otp')    
             


    return render(request,'accounts/otpLogin.html')




def verify_otp(request):
    if request.method=='POST':
        enter_otp=request.POST.get('otp')
        otp=int(enter_otp)
        if request.session.has_key('otp'):
            sended_otp=request.session['otp']
            print(type(sended_otp))
            
            if sended_otp == otp :
                print("in if")
                phone=request.session['phone']
                print(phone)
                user=Account.objects.get(phone_number=phone)
                auth_login(request,user)
                del request.session['otp']
                del request.session['phone']
                
                return redirect('home')
            else:    
                messages.error(request,"entered OTP is wrong")
                return redirect('login_otp') 
        else:
            return redirect('login_otp')          
    return render(request,'accounts/otpLogin.html')            

def checkout_address(request,id):#---------------------------------------------------NOT ADDED-----
    print(id)
    context = {}
    return render(request,'store/favourites.html')
#----------------------------------------------------------------------------------FAVOURITES------------
@login_required(login_url='login')
@never_cache
def favourites(request):
    context = {}
    return render(request,'store/favourites.html')        

#---------------------------------------------------------------------------------PRODUCTS-----------------
@login_required(login_url='login')
@never_cache
def productDetail(request,id):

    obj = Product.objects.get(id=id)

    if  request.user.is_authenticated:
        in_cart =  CartItem.objects.filter(user=request.user,product=obj)

    else :
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=obj)

    
    
    context = {
    'product' : obj,
    'in_cart':in_cart,
    }
    return render(request,'store/productDetail.html',context)

def productFilter(request):
    context = {

    }
    return render(request,'store/productFilter.html',context)

#----------------------------------------------------------------------------------ACCOUNT--------------------
@login_required(login_url='login')
@never_cache
def myAccount(request):
    if UserPropic.objects.filter(user=request.user).exists():
        obj=UserPropic.objects.get(user=request.user)
    else:
        obj = UserPropic()
        obj.user = request.user
        obj.save()

    context = {
        'user' : request.user,
        'proPic': obj,
    }
    return render (request,'store/myAccount.html',context)

def editPropic(request):
    if request.POST.get('pro_img1'):

        current_user = request.user
        pro_pic_instance = UserPropic.objects.get(user = current_user )

        if pro_pic_instance.pro_pic:   #delete previous image from database
            pro_pic_instance.pro_pic.delete()

        image_name = pro_pic_instance.user.email

        cropped_image = request.POST['pro_img1']

        format, img1 = cropped_image.split(';base64,')
        ext = format.split('/')[-1]
        image_data = ContentFile(base64.b64decode(img1), name=image_name + '1.' + ext)

        pro_pic_instance.pro_pic = image_data
        pro_pic_instance.save()

    return redirect('myAccount')

@login_required(login_url='login')
@never_cache
def editAccountDetails(request):
    if UserPropic.objects.filter(user=request.user).exists():
        pro_pic_instance=UserPropic.objects.get(user=request.user)
    else:
        pro_pic_instance = UserPropic()
        pro_pic_instance.user = request.user
        pro_pic_instance.save()  

    if request.method == 'POST':

        current_user = request.user
        account_instance = Account()
        account_instance = current_user

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        if Account.objects.filter(email = email).exists():
            same_email=  Account.objects.get(email = email)
            if same_email.id != account_instance.id :
                messages.error(request,"email already exists")
                return redirect('editAccountDetails')

        if Account.objects.filter(phone_number = phone_number).exists():
            same_phn = Account.objects.get(phone_number = phone_number)
            if same_phn.id != account_instance.id :
                messages.error(request,"phone number already exists")
                return redirect('editAccount')



        account_instance.first_name = first_name
        account_instance.email = email
        account_instance.last_name = last_name
        account_instance.phone_number = phone_number
        account_instance.save()

        #change image
        if request.POST.get('pro_img1'):
            cropped_image = request.POST['pro_img1']

            image_name = pro_pic_instance.user.email
            format, img1 = cropped_image.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(base64.b64decode(img1), name=image_name + '1.' + ext)

            if pro_pic_instance.pro_pic:   #delete previous image from database
                pro_pic_instance.pro_pic.delete()

            pro_pic_instance.pro_pic = image_data
            pro_pic_instance.save()

        return redirect('myAccount')

    context = {
        'user' : request.user,
        'proPic': pro_pic_instance,
    }
    return render (request,'store/editMyAccount.html',context)
#-----------------------------------------------------------------------------ADDRESS----------------
@login_required(login_url='login')
@never_cache
def myAddress(request):
    if UserAddress.objects.filter(user=request.user).exists():
        addresses = UserAddress.objects.filter(user=request.user)
        print("-------------------------------------",addresses)
    else:
        addresses = None
    context = {
        "addresses":addresses,

    }
    return render (request,'store/myAddress.html',context)

@login_required(login_url='login')
@never_cache
def addAddress(request):
    print("in add address================")
    if request.method == 'POST':
        address = UserAddress()
        address.user=request.user
        address.address_name=request.POST.get('address_name')
        address.first_name=request.POST.get('first_name')
        address.last_name=request.POST.get('last_name')
        address.phone=request.POST.get('phone_number')
        address.email=request.POST.get('email')
        address.address_line1=request.POST.get('address_line1')
        address.address_line2=request.POST.get('address_line2')
        address.pin=request.POST.get('pin')
        address.city=request.POST.get('city')
        address.state=request.POST.get('state')
        if UserAddress.objects.filter(user=request.user,address_name = address.address_name).exists():
            return JsonResponse({'status':False,'message':"Address name already exists"})

        
        address.save()
        return JsonResponse({'status':True,'message':"Address Saved"})
    return render (request,'store/addAddress.html')

@login_required(login_url='login')
@never_cache
def editAddress(request,id):
    if request.method == 'POST':
        address = UserAddress(user=request.user,id=id)
        address.user=request.user
        address.address_name=request.POST.get('address_name')
        address.first_name=request.POST.get('first_name')
        address.last_name=request.POST.get('last_name')
        address.phone=request.POST.get('phone_number')
        address.email=request.POST.get('email')
        address.address_line1=request.POST.get('address_line1')
        address.address_line2=request.POST.get('address_line2')
        address.pin=request.POST.get('pin')
        address.city=request.POST.get('city')
        address.state=request.POST.get('state')
        if UserAddress.objects.filter(user=request.user,address_name = address.address_name).exists():
            same_address = UserAddress.objects.get(user=request.user,address_name = address.address_name)
            if same_address.id != id: 
                return JsonResponse({'status':False,'message':"Address name already exists"})

    
        address.save()
        return JsonResponse({'status':True,'message':"Address Updated"})

    else:
        if UserAddress.objects.filter(user=request.user,id=id).exists():
            address=UserAddress.objects.get(user=request.user,id=id)
        else:
            messages.error(request,"address doesnt exists") 
            return redirect('myAddress')


    context = {

    "address":address
    }
    return render (request,'store/editAddress.html',context)        
#-----------------------------------------------------------------------------ORDERS----------------
@login_required(login_url='login')    
@never_cache
def myOrders(request):
    ordered_products = OrderProduct.objects.filter(user=request.user).order_by('-created_at')
    context = {
    "ordered_products" : ordered_products
    }
    return render (request,'store/testmyOrders.html',context) 

@login_required(login_url='login')
@never_cache
def orderDetail(request,id):
    print(id)
    if OrderProduct.objects.filter(id=id).exists():
        ordered_product = OrderProduct.objects.get(id=id)

        if CouponUsed.objects.filter(order_number = ordered_product.order.order_number).exists(): #update couponused if coupon applied to this order
            use_coupon = CouponUsed.objects.get(order_number = ordered_product.order.order_number,is_ordered = True)
            
        else:
            use_coupon= None
    else:
        return redirect('myOrders')
    print(use_coupon,"=======================================used coupon")
    context = {
        "use_coupon":use_coupon,
    "ordered_product" : ordered_product
    }
    return render (request,'store/orderDetail.html',context)   

def cancel_order(request,id):
    print(id)
    if OrderProduct.objects.filter(id=id).exists():
        ordered_product = OrderProduct.objects.get(id=id)
        ordered_product.user_cancelled = True
        ordered_product.save()
    
    return redirect('myOrders')

 #============================generateReferral==============================
def generateReferral(request):
    print("referralGenerate")
    if ReferralUsers.objects.filter(user = request.user).exists():
        code_instance = ReferralUsers.objects.get(user = request.user)
        return  JsonResponse({'code':"http://127.0.0.1:8000/referral/"+code_instance.referral_code,'message':"code given"})

    else:
        code_instance = ReferralUsers()
        code_instance.user = request.user
        code_instance.referral_code=str(uuid.uuid4()).replace("-","")[:12]
        code_instance.save()
        return JsonResponse({'code':"http://127.0.0.1:8000/referral/"+code_instance.referral_code,'message':"code generated"})

