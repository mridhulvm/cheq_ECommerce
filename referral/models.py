from django.db import models
from accounts.models import Account

import datetime


# Create your models here.
class ReferralUsers(models.Model):
    user = models.OneToOneField(Account,on_delete=models.CASCADE) 
    referral_code = models.CharField(max_length=50,blank = True)
    referral_count = models.CharField(max_length=50,default = 0)

    def __str__(self):
        return self.user.username

class ReferralCoupon(models.Model):

    user=models.ForeignKey(Account,on_delete=models.CASCADE)  
    order_number=models.CharField(max_length=100,null=True)

    discount_amount=models.CharField(max_length=50,blank= False,null= False)

    referral_end=models.DateField(blank = False)  
    is_ordered=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def check_expired(self):
        today = datetime.date.today()
        today1 = today.strftime("%Y-%m-%d")
        
        print(str(self.referral_end) < today1,"===============check expired Referral Coupon")

        # return str(self.referral_end_date)<= today1 and self.is_available

        if str(self.referral_end) > today1 and  self.is_available == True :
            return False #not expired
        else:
            return True  #expired


class Referral(models.Model):

    user=models.OneToOneField(Account,on_delete=models.CASCADE) 
    recommended_user=models.ForeignKey(Account,on_delete=models.CASCADE,related_name='ref_by')  

    updated_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)

    referral_code=models.CharField(max_length=50,blank = False)


    def __str__(self):
        return self.user.first_name+" "+self.user.last_name+"--"+self.recommended_user.first_name+" "+self.recommended_user.last_name
    

class ReferralControl(models.Model):

    referral_user_limit=models.CharField(max_length=50,blank = False)
    referral_end_date=models.DateField(null= True)  

    referral_amount=models.CharField(max_length=50,blank = True,null = True)

    is_available = models.BooleanField(default= True)
    updated_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.referral_user_limit  +self.referral_percentage +self.referral_amount
    
    def check_expired(self):
        today = datetime.date.today()
        today1 = today.strftime("%Y-%m-%d")
        
        print(str(self.referral_end_date) < today1,"===============check expired Referral Control")

        # return str(self.referral_end_date)<= today1 and self.is_available

        if str(self.referral_end_date) > today1 and  self.is_available == True :
            return False #not expired
        else:
            return True  #expired

    def check_expired_date_only(self):
        today = datetime.date.today()
        today1 = today.strftime("%Y-%m-%d")
        

        return str(self.referral_end_date) <= today1 

           


            
        