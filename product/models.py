from django.db import models
from django.urls import reverse
from category.models import *
from accounts.models import *


import datetime



# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique= True)
    slug         = models.CharField(max_length = 200, unique= True)
    description  = models.TextField(max_length = 500, blank = True)
    
    price        = models.IntegerField()

    offer_price  = models.IntegerField( null = True,blank=True)
    offer_percentage  = models.IntegerField( null = True,blank=True)
    # offer_available = models.BooleanField(default= False)




    image1       = models.ImageField(upload_to='products',blank = False)
    image2       = models.ImageField(upload_to='products',blank = False)
    image3       = models.ImageField(upload_to='products',blank = False)
    image4       = models.ImageField(upload_to='products',blank = False)

    stock        = models.IntegerField()
    is_available = models.BooleanField(default= True)

    category     = models.ForeignKey(Category,on_delete= models.CASCADE)
    created_date = models.DateTimeField(auto_now_add= True)
    modified_date= models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse("productDetail",kwargs={"id":self.id})

    def __str__(self):
        return self.product_name

    def offer_status(self):
        today = date.today()
        today1 = today.strftime("%Y-%m-%d")

        if ProductOffer.objects.filter(product = self.id).exists():
            offer = ProductOffer.objects.get(product = self.id)
            # print(str(offer.offer_end)>=today1)
            # return str(offer.offer_end)>=today1
            if str(offer.offer_end)<= today1:
                print(" in product Product offer false")
                return False
                
            else:
                print(" in product Product offer true")
                return True 

        if CategoryOffer.objects.filter(id = self.category.id).exists():
            offer = CategoryOffer.objects.get(id = self.category.id)
            if str(offer.offer_end)<= today1:
                print(" in product Category offer true")
                return False
            else:
                print(" in productCategory offer true")
                return True 
        else:
            print("no offer exist false")
            return False  #if no offer added



class ProductOffer(models.Model):
    product=models.OneToOneField(Product,on_delete=models.CASCADE,blank = False)
    offer=models.IntegerField(blank = False)
    offer_start=models.DateField(blank = False)
    offer_end=models.DateField(blank = False)



    def check_expired(self):
        today = date.today()
        today1 = today.strftime("%Y-%m-%d")
        if str(self.offer_end)<= today1:
            return False
        else:
            return True   


class Coupon(models.Model):
    coupon_title=models.CharField(max_length=30,unique=True)  
    coupon_limit=models.IntegerField(blank = False)
    
    coupon_offer=models.FloatField(blank = False)
    coupon_start=models.DateField(blank = False)
    coupon_end=models.DateField(blank = False)  
    is_available = models.BooleanField(default= True)
 

    def check_expired(self):
        today = date.today()
        today1 = today.strftime("%Y-%m-%d")
        
        print(str(self.coupon_end) < today1,"===============check expired Coupon")

        # return str(self.coupon_end)<= today1 and self.is_available

        if str(self.coupon_end) > today1 and  self.is_available == True :
            return False #not expired
        else:
            return True  #expired

    def check_expired_date_only(self):
        today = date.today()
        today1 = today.strftime("%Y-%m-%d")
        

        return str(self.coupon_end) <= today1 

           

class CouponUsed(models.Model):

    user=models.ForeignKey(Account,on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.CASCADE)

    order_number=models.CharField(max_length=100,null=True)

    is_ordered=models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add= True)






