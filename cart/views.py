
from django.shortcuts import redirect, render,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import never_cache

from product.models import Product
from .models import CartItem,Cart
from accounts.models import *
from django.contrib.auth.decorators import login_required

from django.views.decorators.cache import never_cache


import json
from django.http import JsonResponse

from django.http import HttpResponseRedirect  #for   META['HTTP_REFERER']
# Create your views here.

def _cart_id(request):
    print("cart id")
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def minus_cart_ajax(request):
    total =0
    grand_total=0
    tax=0
    product_quantity = 0
    product_id=request.GET.get('product_id')
    print(product_id)
    current_user = request.user
    if current_user.is_authenticated:
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product= product,user=current_user)
        if cart_item.quantity > 1:
            cart_item.quantity -=1 
            cart_item.save()
            product_quantity = cart_item.quantity # setting quantity
            sub_total = cart_item.sub_total()  
          
        else:
            
            cart_item.delete()
            sub_total = 0
        #=========================cart count
        cart_count=0
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart= cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity

                #calculate subtotal tax and grand total====================
                if  cart_item.offer_status() : #check if offer price exists
                    print("offer cart added in ajax")
                    total += (cart_item.product.offer_price * cart_item.quantity)
                else:
                    total += (cart_item.product.price * cart_item.quantity)
                    print("original price cart added in ajax") 
            tax = int ( (2 * total)/100  )
            grand_total = total + tax
                 
        except Cart.DoesNotExist:
            cart_count = 0              
        return JsonResponse({'status':True,'message':"Product Deducted to Cart Succesfully",'cart_count':cart_count,'sub_total':sub_total,'product_quantity':product_quantity,'total':total,'tax':tax,'grand_total':grand_total})
  
    else: #user not authenticated==============================
        cart = Cart.objects.get(cart_id= _cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product= product,cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -=1 
            cart_item.save()
            product_quantity = cart_item.quantity # setting quantity
            sub_total = cart_item.sub_total()  
        else:
            cart_item.delete()
            sub_total = 0
        #=========================cart count
        cart_count=0
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart= cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                #calculate subtotal tax and grand total====================
                if  cart_item.offer_status() : #check if offer price exists
                    print("offer cart added in ajax")
                    total += (cart_item.product.offer_price * cart_item.quantity)
                else:
                    total += (cart_item.product.price * cart_item.quantity)
                    print("original price cart added in ajax") 
            tax = int ( (2 * total)/100  )
            grand_total = total + tax
                                 
        except Cart.DoesNotExist:
            cart_count = 0  
        return JsonResponse({'status':True,'message':"Product Deducted to Cart Succesfully",'cart_count':cart_count,'sub_total':sub_total,'product_quantity':product_quantity,'total':total,'tax':tax,'grand_total':grand_total})
  
def add_cart_ajax(request):

    product_id=request.GET.get('product_id')
    if  request.GET.get('product_quantity'):
        product_quantity_input = int( request.GET.get('product_quantity') )
    else: 
        product_quantity_input = 1

    print(product_id,"=============product_id")
    total =0
    grand_total=0
    tax=0    
    product_quantity = 0
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    if product.stock <1 :
        return JsonResponse({'status':False,'message':"Product Out Of Stock"})

    #if user is authenticated
    if current_user.is_authenticated:
      
        if CartItem.objects.filter(product=product, user=current_user).exists():
            cart_item = CartItem.objects.get(product=product, user=current_user)
            cart_item.quantity += product_quantity_input #custom quantity updation
            cart_item.save()
            product_quantity = cart_item.quantity # setting quantity
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = product_quantity_input,   #custom quantity updation
                user = current_user,
            )
            product_quantity = 1   # setting quantity
            cart_item.save()
        sub_total = cart_item.sub_total()  
        #=========================cart count
        cart_count=0
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart= cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                #calculate subtotal tax and grand total====================
                if  cart_item.offer_status() : #check if offer price exists
                    print("offer cart added in ajax")
                    total += (cart_item.product.offer_price * cart_item.quantity)
                else:
                    total += (cart_item.product.price * cart_item.quantity)
                    print("original price cart added in ajax") 
            tax = int ( (2 * total)/100  )
            grand_total = total + tax                
        except Cart.DoesNotExist:
            cart_count = 0  
        
        return JsonResponse({'status':True,'message':"Product Added to Cart Succesfully",'cart_count':cart_count,'sub_total':sub_total,'product_quantity':product_quantity,'total':total,'tax':tax,'grand_total':grand_total})
    

    #if user is not autheticated
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += product_quantity_input      #custom quantity updation
            cart_item.save()
            product_quantity = cart_item.quantity 

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = product_quantity_input,     #custom quantity updation
                cart = cart,
            )
            product_quantity = 1

            cart_item.save()
        sub_total = cart_item.sub_total()  
        #=========================cart count
        cart_count=0
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                cart_items = CartItem.objects.all().filter(cart= cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity
                #calculate subtotal tax and grand total====================
                if  cart_item.offer_status() : #check if offer price exists
                    print("offer cart added in ajax")
                    total += (cart_item.product.offer_price * cart_item.quantity)
                else:
                    total += (cart_item.product.price * cart_item.quantity)
                    print("original price cart added in ajax") 
            tax = int ( (2 * total)/100  )
            grand_total = total + tax                
        except Cart.DoesNotExist:
            cart_count = 0
        
        return JsonResponse({'status':True,'message':"Product Added to Cart  Succesfully",'cart_count':cart_count,'sub_total':sub_total,'product_quantity':product_quantity,'total':total,'tax':tax,'grand_total':grand_total})

#============================ajax functions ends========================
@never_cache
def add_cart(request, product_id):
    print("add cart")
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    if product.stock <1 :
        return redirect(request.META['HTTP_REFERER'])

    #if user is authenticated
    if current_user.is_authenticated:
      
        if CartItem.objects.filter(product=product, user=current_user).exists():
            cart_item = CartItem.objects.get(product=product, user=current_user)
            cart_item.quantity += 1
            cart_item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            cart_item.save()
        return redirect(request.META['HTTP_REFERER'])
    

    #if user is not autheticated
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            cart_item.quantity += 1
            cart_item.save()

        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            cart_item.save()
        return redirect(request.META['HTTP_REFERER'])

def minus_cart(request,product_id):
    current_user = request.user
    if current_user.is_authenticated:
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product= product,user=current_user)
        if cart_item.quantity > 1:
            cart_item.quantity -=1 
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')

    else:
        cart = Cart.objects.get(cart_id= _cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product= product,cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -=1 
            cart_item.save()
        else:
            cart_item.delete()
        return redirect('cart')


def delete_cart(request,product_id):
    current_user = request.user
    if current_user.is_authenticated:
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product=product,user=current_user)
        cart_item.delete()
        return redirect('cart')
    else:
        cart= Cart.objects.get(cart_id= _cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product=product,cart=cart)
        cart_item.delete()
        return redirect('cart')

    
def cart(request, total=0, quantity=0, cart_items=None):
    print("cart function")
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True,)#check cart items 
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #else 
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:

            if  cart_item.offer_status() : #check if offer price exists
                print("offer cart added in ajax")
                total += (cart_item.product.offer_price * cart_item.quantity)
            else:
                total += (cart_item.product.price * cart_item.quantity)
                print("original price cart added in ajax")

            quantity += cart_item.quantity
        tax = int ( (2 * total)/100  )
        grand_total = total + tax

    except ObjectDoesNotExist:
        total=0
        grand_total=0
        tax=0
        quantity=0
        cart_items=0
    print(total,"------------------total------------------")

    context = {
        'total': total,
        'grand_total':grand_total,
        'tax': tax,
        'quantity': quantity,
        'cart_items': cart_items,
     
    }
    return render(request,'store/cart.html',context) 


#-----------------------------------------------------------------CHECKOUT-----------------


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        current_user = request.user
        cart_items = CartItem.objects.filter(user=current_user, is_active=True)
        for cart_item in cart_items:

            if cart_item.offer_status()  : #check if offer price exists
                total += (cart_item.product.offer_price * cart_item.quantity)
            else:
                total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = int ( (2 * total)/100  )
        grand_total = total + tax

    except ObjectDoesNotExist:
        total=0
        grand_total=0
        tax=0
        quantity=0
        cart_items=0

    if UserAddress.objects.filter(user=request.user).exists():
        addresses = UserAddress.objects.filter(user=request.user)
    else:
        addresses = None   
    print("--------------------------------------------",grand_total)
    if grand_total < 0 :
        return redirect ('cart')
    context = {
        'total': total,
        'grand_total':grand_total,
        'tax': tax,
        'quantity': quantity,
        'cart_items': cart_items,
        'addresses':addresses,
     
    }
    return render(request,'store/checkout.html',context)


def minus_checkout(request,product_id):
    current_user = request.user
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product= product,user=current_user)
    if cart_item.quantity > 1:
        cart_item.quantity -=1 
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('checkout')


def add_checkout(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product

    if CartItem.objects.filter(product=product, user=current_user).exists():
        cart_item = CartItem.objects.get(product=product, user=current_user)
        cart_item.quantity += 1
        cart_item.save()

    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            user = current_user,
        )
        cart_item.save()
    return redirect('checkout')


    