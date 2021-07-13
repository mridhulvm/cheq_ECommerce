from product.models import Product
from orders.models import Order
from django.shortcuts import redirect, render
from .forms import OrderForm
import datetime
import json
from django.http import JsonResponse
import razorpay
from django.views.decorators.csrf import csrf_exempt


from cart.models import CartItem
from .models import Order,Payment,OrderProduct

from django.contrib import messages,auth


# Create your views here.

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
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity  

    tax  = (2 * total)/100
    grand_total = total + tax

    if Order.objects.filter(user=current_user,is_ordered=False):
        data = Order.objects.get(user=current_user,is_ordered=False)
    else:
        data = Order()



    if request.method == 'POST':
        print("post")    

        #store all the billing information inside Order table
        data.user = current_user
        data.first_name =request.POST.get('first_name')
        data.last_name =request.POST.get('last_name')
        data.phone =request.POST.get('phone')
        data.email =request.POST.get('email')
        data.address_line1 =request.POST.get('address1')
        data.address_line2 =request.POST.get('address2')
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
        order = Order.objects.get(user=current_user ,is_ordered=False ,order_number=order_number)
        dollar_total = round(grand_total/74.36,2)
        razoypay_amount=grand_total*100
        context = {
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
    if Order.objects.get(user=request.user,is_ordered=False,order_number=order_number).exists():
        order=Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    grand_total=0
    tax=0
    for cart_item in cart_items:
        total+=(cart_item.product.price * cart_item.quantity) 

    print(total)
    tax = (2*total)/100
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
       
        cart_items.delete()

        return redirect('orderConfirm',order_number=order_number)

 

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
    #move the cart items to order product table
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    for item in cart_items :
        ordered_product=OrderProduct()
        ordered_product.order=order
        ordered_product.payment=payment
        ordered_product.user=request.user
        ordered_product.product=item.product
        ordered_product.quantity=item.quantity
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
    messages.info(request, 'Your Order has been successfully placed')

    for ordered_one_product in ordered_product:
        total += ordered_one_product.product_price

    tax = order_instance.tax
    grand_total= order_instance.order_total

    dollar_total = round(grand_total/74.36,2)

    print( "payment----", payment.payment_method,
    'order---', order_instance,
    'ordered_product---', ordered_product,
    'total--------', total,
    'tax----', tax,
    'grand_total----', grand_total,
    'dollar_total---',dollar_total)

    context = {
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
        total+=(cart_item.product.price * cart_item.quantity) 

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
    
    cart_items.delete()

    return redirect('orderConfirm',order_number=order_number)