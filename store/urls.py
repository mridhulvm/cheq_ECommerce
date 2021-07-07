from django.urls import path
from . import views
 
urlpatterns = [
     path('',views.home,name="home"),

     path('signup',views.signup,name='signup'),
     path('login',views.login,name='login'),
     path('login_otp',views.login_otp,name='login_otp'),
     path('verify_otp',views.verify_otp,name='verify_otp'),

     path('signout',views.signout,name='signout'),

     path('checkout',views.checkout,name="checkout"),
     path('favourites',views.favourites,name="favourites"),
     path('myAccount',views.myAccount,name="myAccount"),
     path('editPropic/<int:id>',views.editPropic,name="editPropic"),


     
     path('productFilter',views.productFilter,name="productFilter"),
     path('productDetail/<int:id>',views.productDetail,name="productDetail"),


]