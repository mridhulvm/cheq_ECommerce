from django.urls import path 
from . import views

urlpatterns = [
    path('placeOrder/',views.placeOrder,name='placeOrder'),
    path('payments/<int:order_number>',views.payments,name='payments'),


]