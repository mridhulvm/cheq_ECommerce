from django.urls import path
from . import views
 
urlpatterns = [
     path('',views.home,name="home"),

     path('signup',views.signup,name='signup'),
     path('login',views.login,name='login'),
     path('login_otp',views.login_otp,name='login_otp'),
     path('verify_otp',views.verify_otp,name='verify_otp'),

     path('signout',views.signout,name='signout'),

     path('checkout_address/<int:id>',views.checkout_address,name="checkout_address"),#not added
     path('favourites',views.favourites,name="favourites"),
     path('myAccount',views.myAccount,name="myAccount"),
     path('myAddress',views.myAddress,name="myAddress"),
     path('myOrders',views.myOrders,name="myOrders"),

     path('generateReferral',views.generateReferral,name="generateReferral"),



     path('orderDetail/<int:id>',views.orderDetail,name="orderDetail"),
     path('cancel_order/<int:id>',views.cancel_order,name="cancel_order"),


     path('editAccountDetails',views.editAccountDetails,name="editAccountDetails"),
     path('editPropic',views.editPropic,name="editPropic"),

     path('addAddress',views.addAddress,name="addAddress"),
     path('editAddress/<int:id>',views.editAddress,name="editAddress"),


     
     path('productFilter',views.productFilter,name="productFilter"),
     path('productDetail/<int:id>',views.productDetail,name="productDetail"),



]