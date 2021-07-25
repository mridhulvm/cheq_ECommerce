from product.models import Product
from orders.models import Order
from django.shortcuts import redirect, render
from .forms import OrderForm
import datetime
import math 
import json
from django.http import JsonResponse

import razorpay
from django.views.decorators.csrf import csrf_exempt


from cart.models import CartItem
from .models import Order,Payment,OrderProduct
from product.models import *
from referral.models import ReferralCoupon
from django.contrib import messages,auth


# Create your views here.
def checkCoupon(request):

    if request.method=='GET':
        data=request.GET.get('data')
        grand_total=int(request.GET.get('grand_total'))
        print(data,"========================================",grand_total)
        if Coupon.objects.filter(coupon_title=data).exists():
            coupon_instance=Coupon.objects.get(coupon_title=data)

            print("============coupon expired=====",coupon_instance.check_expired() )

            if coupon_instance.check_expired() :
                return JsonResponse({'status':True,'message':"Coupon Expired"})

            if CouponUsed.objects.filter(user=request.user,coupon=coupon_instance ,is_ordered = True).exists():
                return JsonResponse({'status':True,'message':"Coupon already used" })

            elif CouponUsed.objects.filter(user=request.user,coupon=coupon_instance ,is_ordered = False).exists():
               use_coupon=CouponUsed.objects.get(user=request.user,coupon=coupon_instance)
               
            else:
               use_coupon=CouponUsed()

            use_coupon.user = request.user
            use_coupon.coupon = coupon_instance
            use_coupon.save()

            print(grand_total,coupon_instance.coupon_offer)

            percent_value = int(grand_total)*(100 - int(coupon_instance.coupon_offer) )/100
            if percent_value > coupon_instance.coupon_limit:
                grand_total = int(grand_total )- int(coupon_instance.coupon_limit)
                coupon_price = int(coupon_instance.coupon_limit)
            else:
                grand_total = grand_total - int(percent_value)
                coupon_price = int(percent_value )
                
            if request.session.get('REFERRAL_id'):#delete  referral session if applied coupon
                del request.session['REFERRAL_id']

            return JsonResponse({'status':False,'message':"Coupon applied" ,'grand_total':grand_total,'coupon_price':coupon_price})

        elif data =="REFERRAL": #referral=============================================================================
            if ReferralCoupon.objects.filter(user = request.user).exists():

                if ReferralCoupon.objects.filter(user = request.user,is_ordered = False).exists():
                    coupon_instance = ReferralCoupon.objects.filter(user = request.user,is_ordered = False).first()   
                    print("first coupon===",coupon_instance)

                    if coupon_instance.check_expired == True:
                        return JsonResponse({'status':True,'message':"Referral Coupon Expired"})

                    grand_total = grand_total - int(coupon_instance.discount_amount)
                    coupon_price = int(coupon_instance.discount_amount)

                    if request.session.get('REFERRAL_id'):#add value id to referral session
                        del request.session['REFERRAL_id']
                    request.session['REFERRAL_id']=coupon_instance.id
                    print(request.session.get('REFERRAL_id'))

                    return JsonResponse({'status':False,'message':"Referral Coupon applied" ,'grand_total':grand_total,'coupon_price':coupon_price})
                else:
                    return JsonResponse({'status':True,'message':"Referral Coupon used" })    

            else:
                return JsonResponse({'status':True,'message':"Referral Coupon Unavailable" })
        else:
            print("returntrue,invalid coupon=====================")
            return JsonResponse({'status':True,'message':"Invalid Coupon"})

def retrieveCouponWithTitle(request,grand_total,data):

    print(data,"==============data==========================",grand_total)
    coupon_instance=Coupon.objects.get(coupon_title=data)

    if CouponUsed.objects.filter(user=request.user,coupon=coupon_instance ,is_ordered = False).exists():
        use_coupon=CouponUsed.objects.get(user=request.user,coupon=coupon_instance)
        
    else:
        use_coupon=CouponUsed()

    use_coupon.user = request.user
    use_coupon.coupon = coupon_instance
    use_coupon.save()

    print(grand_total,coupon_instance.coupon_offer)

    percent_value = int(grand_total)*int(coupon_instance.coupon_offer) /100

    if percent_value > coupon_instance.coupon_limit:
        grand_total = int(grand_total )- int(coupon_instance.coupon_limit)
        coupon_price = int(coupon_instance.coupon_limit)
    else:
        grand_total = grand_total - int(percent_value)
        coupon_price = int(percent_value )
    
    return grand_total,coupon_price,use_coupon.id
            
    
def checkCouponStatus(request,data):
        print(data,"=========================checkCouponStatus===============")
        if Coupon.objects.filter(coupon_title=data).exists():
            coupon_instance=Coupon.objects.get(coupon_title=data)

            if coupon_instance.check_expired() :
                print("======================= coupon expired=========")
                return False

            if CouponUsed.objects.filter(user=request.user,coupon=coupon_instance ,is_ordered = True).exists():
                print("=======================IS ORDERED TRUE=========")

                return False

            print("=======================Offer valid=========")

            
            return True
            
        else:
            return False

def placeOrder(request, total=0, quantity=0,):
    current_user = request.user

    #if the cart count is less then or equal to 0 ,then redirect
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('cart')

    grand_total = 0
    tax = 0

    for cart_item in cart_items:

        if cart_item.offer_status() : #check if offer price exists
            total += (cart_item.product.offer_price * cart_item.quantity)
        else:
            total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity  

    tax  = int ( (2 * total)/100 )
    grand_total = total + tax


    if Order.objects.filter(user=current_user,is_ordered=False):
        data = Order.objects.get(user=current_user,is_ordered=False)
    else:
        data = Order()



    if request.method == 'POST':
        print("post")    

        #store all the billing information inside Order table


        if request.POST.get('coupon_title') and request.POST.get('coupon_title') != "REFERRAL":  #for coupon check and retrieve grandtotal and coupon price
            coupon_title=request.POST.get('coupon_title')
            if checkCouponStatus(request, coupon_title):
                print(coupon_title,"===========================checkCouponStatus====Passed")

                grand_total,coupon_price,use_coupon_id = retrieveCouponWithTitle(request,grand_total,coupon_title)

                print(grand_total,coupon_price,"=============================coupon price")

                data.coupon_price = coupon_price
                use_coupon = CouponUsed.objects.get(id =use_coupon_id)

        elif request.session.get('REFERRAL_id'):#add value id to referral coupon
            coupon_instance = ReferralCoupon.objects.filter(user = request.user,is_ordered = False).first()   
            grand_total = grand_total - int(coupon_instance.discount_amount)
            data.coupon_price = int(coupon_instance.discount_amount)
            coupon_price = int(coupon_instance.discount_amount) #for passing html page

        else:
            data.coupon_price = 0



        data.user = current_user
        data.first_name =request.POST.get('first_name')
        data.last_name =request.POST.get('last_name')
        data.phone =request.POST.get('phone')
        data.email =request.POST.get('email')
        data.address_line1 =request.POST.get('address1')
        data.address_line2 =request.POST.get('address2')
        data.pin =request.POST.get('pin')

        data.state =request.POST.get('state')
        data.city =request.POST.get('city')
        data.order_note =request.POST.get('order_note')
        data.order_total = grand_total
        data.tax = tax 
        data.ip  = request.META.get('REMOTE_ADDR')

        data.save()
        # Generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")

        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        if request.POST.get('coupon_title') and request.POST.get('coupon_title') != "REFERRAL":  #add order number to coupon used
            # if checkCouponStatus(request, coupon_title):

            use_coupon.order_number = data.order_number
            use_coupon.save()
            # else:
            #     coupon_price = None

        elif request.session.get('REFERRAL_id'):#add order number to referral coupon
            coupon_instance.order_number = data.order_number
            coupon_instance.save()
            
        else:
            coupon_price = None

        order = Order.objects.get(user=current_user ,is_ordered=False ,order_number=order_number)
        dollar_total = round(grand_total/74.36,2)
        razoypay_amount=grand_total*100
        context = {
            'coupon_price' :coupon_price,
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'razoypay_amount':razoypay_amount,
                'dollar_total':dollar_total,

            }
        return render(request,'store/payments.html',context) 
    else:
        return redirect('checkout')

def payments(request,order_number,total=0):

    if Order.objects.filter(user=request.user,is_ordered=False,order_number=order_number).exists():
        order=Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    grand_total=0
    tax=0
    for cart_item in cart_items:
        if cart_item.offer_status() : #check if offer price exists
            total += (cart_item.product.offer_price * cart_item.quantity)
        else:
            total += (cart_item.product.price * cart_item.quantity)

    print(total)
    tax = int ( (2*total)/100 )
    grand_total= total+tax 
    payment_method = request.POST.get('payment-option')

    if payment_method == 'cash_on_delivery':
        payment = Payment(user=request.user,payment_id=order_number,payment_method="COD",amount_paid=grand_total,satus="completed")
        payment.save()
        for item in cart_items :
            ordered_product=OrderProduct()
            ordered_product.order=order
            ordered_product.payment=payment
            ordered_product.user=request.user
            ordered_product.product=item.product
            ordered_product.quantity=item.quantity

            if item.offer_status() : #check if offer price exists
                ordered_product.product_price = item.product.offer_price 
            else:
                ordered_product.product_price = item.product.price
            ordered_product.ordered = True
            ordered_product.status = "Ordered"
            ordered_product.save()
            #reduce stock
            product=Product.objects.get(id=item.product_id)        
            product.stock -= item.quantity
            product.save()            
        
        order.is_ordered=True
        order.payment = payment
        order.save()
        if CouponUsed.objects.filter(order_number =order.order_number).exists(): #update couponused if coupon applied to this order
            use_coupon = CouponUsed.objects.get(order_number =order.order_number)
            use_coupon.is_ordered = True
            use_coupon.save()
        if ReferralCoupon.objects.filter(order_number =order.order_number).exists(): #update referral coupon
            use_coupon = ReferralCoupon.objects.get(order_number =order.order_number)
            use_coupon.is_ordered = True
            use_coupon.save()

            if request.session.get('REFERRAL_id'):#delete referral session
                    del request.session['REFERRAL_id']

        cart_items.delete()

        return redirect('orderConfirm', order_number)
    else:
        return redirect('placeOrder')


 

def paypal(request):
    print("paypal")
    body = json.loads(request.body)
    print(body)
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])
    #store transaction details inside payment model
    payment=Payment(user=request.user,payment_id=body['trans_ID'],payment_method=body['payment_method'],amount_paid=order.order_total,satus=body['status'])
    payment.save()

    order.payment=payment
    order.is_ordered=True
    order.save()

    if CouponUsed.objects.filter(order_number =order.order_number).exists(): #update couponused if coupon applied to this order
        use_coupon = CouponUsed.objects.get(order_number =order.order_number)
        use_coupon.is_ordered = True
        use_coupon.save()

    if ReferralCoupon.objects.filter(order_number =order.order_number).exists(): #update referral coupon corresponding to this order
        use_coupon = ReferralCoupon.objects.get(order_number =order.order_number)
        use_coupon.is_ordered = True
        use_coupon.save()

        if request.session.get('REFERRAL_id'):#delete referral session
                del request.session['REFERRAL_id']


    #move the cart items to order product table
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    for item in cart_items :
        ordered_product=OrderProduct()
        ordered_product.order=order
        ordered_product.payment=payment
        ordered_product.user=request.user
        ordered_product.product=item.product
        ordered_product.quantity=item.quantity

        if item.offer_status() : #check if offer price exists
            ordered_product.product_price = item.product.offer_price 
        else:
            ordered_product.product_price = item.product.price

        ordered_product.ordered = True
        ordered_product.status = "Ordered"
        ordered_product.save()
        #reduce stock
        product=Product.objects.get(id=item.product.id)        
        product.stock -= item.quantity
        product.save()

    #clear the cart
    cart_items.delete()

    data={
        'order_number':order.order_number,
        'trans_ID':payment.payment_id
    }   

    return JsonResponse(data)



def orderConfirm(request,order_number,total=0):
    print(order_number)
    order_instance=Order.objects.get(user=request.user,order_number=order_number)
    payment = order_instance.payment
    
    ordered_product = OrderProduct.objects.filter(payment=payment)
    # messages.info(request, 'Your Order has been successfully placed')

    for ordered_one_product in ordered_product:
        if ordered_one_product.product.offer_status() : #check if offer price exists
            total += (ordered_one_product.product.offer_price * ordered_one_product.quantity)
        else:
            total += (ordered_one_product.product.price * ordered_one_product.quantity)       
        # total += ordered_one_product.product_price

    tax = int(order_instance.tax)
    grand_total= int(order_instance.order_total)

    dollar_total = round(grand_total/74.36,2)

    print( "payment----", payment.payment_method,
    'order---', order_instance,
    'ordered_product---', ordered_product,
    'total--------', total,
    'tax----', tax,
    'grand_total----', grand_total,
    'dollar_total---',dollar_total)

    context = {
        'coupon_price': order_instance.coupon_price,
        "payment": payment.payment_method,
        'order': order_instance,
        'ordered_product': ordered_product,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'dollar_total':dollar_total,
    }
    return render(request,'store/orderConfirm.html',context) 


def razorpay(request,order_number,total=0):
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    grand_total=0
    tax=0

    for cart_item in cart_items:
        if cart_item.offer_status() : #check if offer price exists
            total += (cart_item.product.offer_price * cart_item.quantity)
        else:
            total += (cart_item.product.price * cart_item.quantity)

    print(total)
    tax = (2*total)/100
    grand_total= total+tax 
    payment = Payment(user=request.user,payment_id=order_number,payment_method="Razorpay",amount_paid=grand_total,satus="COMPLETED")
    payment.save()
    for item in cart_items :
        ordered_product=OrderProduct()
        ordered_product.order=order
        ordered_product.payment=payment
        ordered_product.user=request.user
        ordered_product.product=item.product
        ordered_product.quantity=item.quantity

        if item.offer_status() : #check if offer price exists
            ordered_product.product_price = item.product.offer_price 
        else:
            ordered_product.product_price = item.product.price  

        ordered_product.ordered = True
        ordered_product.status = "Ordered"
        ordered_product.save()
        #reduce stock
        product=Product.objects.get(id=item.product_id)        
        product.stock -= item.quantity
        product.save()            
    
    order.is_ordered=True
    order.payment_id = payment.id
    order.save()

    if CouponUsed.objects.filter(order_number =order.order_number).exists(): #update couponused if coupon applied to this order
        use_coupon = CouponUsed.objects.get(order_number =order.order_number)
        use_coupon.is_ordered = True
        use_coupon.save()

    if ReferralCoupon.objects.filter(order_number =order.order_number).exists(): #update referral coupon corresponding to this order
        use_coupon = ReferralCoupon.objects.get(order_number =order.order_number)
        use_coupon.is_ordered = True
        use_coupon.save()

        if request.session.get('REFERRAL_id'):#delete referral session
                del request.session['REFERRAL_id']

    cart_items.delete()

    return redirect('orderConfirm',order_number=order_number)