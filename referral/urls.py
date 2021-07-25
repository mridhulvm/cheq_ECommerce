from django.urls import path
from . import views
 
urlpatterns = [

     path('<str:referral_code>',views.referralSignup,name="referralSignup"),
]