from orders.models import Order
from django.shortcuts import redirect, render
from .forms import OrderForm
import datetime

from cart.models import CartItem
from .models import Order,Payment,OrderProduct

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

    if request.method == 'POST':
        print("post")    

        #store all the billing information inside Order table
        data = Order()
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
        context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
        return render(request,'store/payments.html',context) 
    else:
        return redirect('checkout')

def payments(request,order_number,total=0):
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
    cart_items=CartItem.objects.filter(user=request.user,is_active=True)
    grand_total=0
    tax=0
    for cart_item in cart_items:
        total+=(cart_item.product.price * cart_item.quantity) 

    print(total)
    tax = (2*total)/100
    grand_total= total+tax 
    if request.POST.get('cash_on_delivery'):
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
            ordered_product.status = "ordered"
            ordered_product.save()
            context = {
                "payment": payment.payment_method,
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            cart_items.delete()
            return render(request,'store/orderConfirm.html',context) 


