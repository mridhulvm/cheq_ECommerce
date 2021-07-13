from django.urls import path 
from . import views

urlpatterns = [
    path('placeOrder',views.placeOrder,name='placeOrder'),
    path('payments/<int:order_number>',views.payments,name='payments'),

    path('paypal',views.paypal,name='paypal'),
    path('razorpay/<int:order_number>',views.razorpay,name='razorpay'),

    
    path('orderConfirm/<int:order_number>',views.orderConfirm,name='orderConfirm'),





]