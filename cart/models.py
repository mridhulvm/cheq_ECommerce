from django.db import models
from accounts.models import Account
from product.models import Product,ProductOffer
from category.models import CategoryOffer
from datetime import date


# Create your models here.

class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    date_added= models.DateField(auto_now_add=True)


    def __str__(self):
        return self.cart_id



class CartItem(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE) 
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField()
    is_active=models.BooleanField(default=True) 


    def sub_total(self): 
        # var = self.offer_status1
        # print(var)
        # if var != False :
        #     print("offer_price")
        #     return self.product.offer_price * self.quantity

        # else:   
        #     print("price added")
        #     return self.product.price * self.quantity
        today = date.today()
        today1 = today.strftime("%Y-%m-%d")

        if ProductOffer.objects.filter(product = self.product).exists():
            offer = ProductOffer.objects.get(product = self.product)
            
            if str(offer.offer_end)<= today1:
                print("Product offer false")
                return self.product.price * self.quantity
                
            else:
                print("Product offer true")
                return self.product.offer_price * self.quantity

        if CategoryOffer.objects.filter(category = self.product.category).exists():
            offer = CategoryOffer.objects.get(category = self.product.category)
            if str(offer.offer_end)<= today1:
                print("Category offer true")
                return self.product.price * self.quantity
            else:
                print("Category offer true")
                return self.product.offer_price * self.quantity
        else:
            print("no offer exist false")
            return self.product.price * self.quantity #if no offer added            
      

    def offer_status(self):
        today = date.today()
        today1 = today.strftime("%Y-%m-%d")

        if ProductOffer.objects.filter(product = self.product).exists():
            offer = ProductOffer.objects.get(product = self.product)
            
            if str(offer.offer_end)<= today1:
                print("Product offer false")
                return False
                
            else:
                print("Product offer true")
                return True 

        if CategoryOffer.objects.filter(id = self.product.category.id).exists():
            offer = CategoryOffer.objects.get(id = self.product.category.id)
            if str(offer.offer_end)<= today1:
                print("Category offer true")
                return False
            else:
                print("Category offer true")
                return True 
        else:
            print("no offer exist false")
            return False  #if no offer added

    def __str__(self):
            return self.product