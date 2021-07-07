from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login as auth_login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from twilio.rest import Client
import random



from django.contrib import messages,auth

from cart.views import _cart_id
from cart.models import Cart,CartItem

from product.models import Product
from category.models import Category
from accounts.models import Account,UserPropic

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


def login_otp(request):
    if request.method=='POST':
        phone=request.POST['phone_number']
        if Account.objects.filter(phone_number=phone).exists():
            otp = random.randint(100000,999999)
            strotp=str(otp)
            account_sid ='ACca48f33a1a36f7da7d530b7397521bde'
            auth_token ='df525d6f373b3ac76820539225e241ca'
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

@login_required(login_url='login')
@never_cache
def favourites(request):
    context = {}
    return render(request,'store/favourites.html')        


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

def editPropic(request,id):
    if request.method == 'POST':
        pass