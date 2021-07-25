from django.urls import path
from . import views
 
urlpatterns = [

    path('',views.cart,name="cart"),
    path('add_cart/<int:product_id>/',views.add_cart,name="add_cart"),
    
    path('add_cart_ajax',views.add_cart_ajax,name="add_cart_ajax"),
    path('minus_cart_ajax',views.minus_cart_ajax,name="minus_cart_ajax"),

    path('minus_cart/<int:product_id>/',views.minus_cart,name="minus_cart"),
    path('delete_cart/<int:product_id>/',views.delete_cart,name="delete_cart"),

    path('checkout',views.checkout,name='checkout'),
    path('add_checkout/<int:product_id>/',views.add_checkout,name="add_checkout"),
    path('minus_checkout/<int:product_id>/',views.minus_checkout,name="minus_checkout"),



]
