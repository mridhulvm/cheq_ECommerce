from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login as auth_login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from twilio.rest import Client
import random

from django.core.files.base import ContentFile #base 64 to image conversion
import base64



from django.contrib import messages,auth

from cart.views import _cart_id
from cart.models import Cart,CartItem

from product.models import Product
from category.models import Category
from accounts.models import Account,UserPropic
from orders.models import *

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

        username = email.split('@')[0]
        cpassword=request.POST.get('confirm_password')
        print(username)
        if cpassword != password:
            print("password mismatch")
            messages.info(request, 'password mismatch')
            return redirect('signup')
        if len(phone_number) != 10 :
            messages.info(request, 'Enter a valid Phone number')
            return redirect('signup')
            # context = {
            # 'form': form
            # }
            # return render(request,'accounts/signup.html')
        if Account.objects.filter(phone_number=phone_number).exists():
            messages.info(request, 'phone number already exists')
            print("phone")
            return redirect('signup')

        if Account.objects.filter(email=email).exists() :
            messages.info(request, 'email already exists')
            print("email")
            return redirect('signup')


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
            messages.info(request, 'You are registered')

    # else:
    #     form = AccountForm()

    # context = {
    #     'form': form
    # }
    return render(request,'accounts/register.html')



def signout(request):
    logout(request)
    return redirect('/') 

def login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = email.split('@')[0]

        user = authenticate(username=username,password=password)
        print("----------------------------------------------------------------",user)
        if Account.objects.filter(email=email,password=password).exists() :
            obj = Account.objects.get(email=email,password=password)
            if obj.is_active != True:
                messages.info(request, 'Your account has been blocked')
                return render(request,'accounts/login.html')
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
            return redirect('home')
        else:
            messages.info(request, 'Invalid username or password')
    return render(request,'accounts/login.html')
#---------------------------------------------------------------------------OTP LOGIN------------------

def login_otp(request):
    if request.method=='POST':
        phone=request.POST['phone_number']
        if Account.objects.filter(phone_number=phone).exists():
            otp = random.randint(100000,999999)
            strotp=str(otp)
            account_sid ='A'
            auth_token ='d'
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

def checkout(request):
    context = {}
    return render(request,'store/checkout.html')
#----------------------------------------------------------------------------------FAVOURITES------------
@login_required(login_url='login')
@never_cache
def favourites(request):
    context = {}
    return render(request,'store/favourites.html')        

#---------------------------------------------------------------------------------PRODUCTS-----------------
def productDetail(request,id):
    obj = Product.objects.get(id=id)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=obj).exists()
    print(obj,in_cart)
    
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


def editAccountDetails(request):
    if UserPropic.objects.filter(user=request.user).exists():
        pro_pic_instance=UserPropic.objects.get(user=request.user)
    else:
        pro_pic_instance = UserPropic()
        pro_pic_instance.user = request.user
        pro_pic_instance.save()  

    if request.method == 'POST':
<<<<<<< HEAD

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
                return redirect('editAccount')

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
def myAddress(request):
    context = {

    }
    return render (request,'store/myAddress.html',context)

def addAddress(request):
    context = {

    }
    return render (request,'store/myAddress.html',context)

def editAddress(request):
    context = {

    }
    return render (request,'store/myAddress.html',context)        
#-----------------------------------------------------------------------------ORDERS----------------
    
def myOrders(request):
    ordered_products = OrderProduct.objects.filter(user=request.user)
    print(ordered_products)
    context = {
    "ordered_products" : ordered_products
    }
    return render (request,'store/myOrders.html',context)    

def orderDetail(request,id):
    print(id)
    if OrderProduct.objects.filter(id=id).exists():
        ordered_product = OrderProduct.objects.get(id=id)
    else:
        return redirect('myOrders')

    context = {
    "ordered_product" : ordered_product
    }
    return render (request,'store/orderDetail.html',context)   
=======
        pass
>>>>>>> 9b4781074b8eb4a8ada9a794c2b732fc60a439f9
