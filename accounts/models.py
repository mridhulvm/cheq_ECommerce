from django.db import models
from django.contrib.auth.models import AbstractBaseUser,AbstractUser
# ,BaseUserManager


# class MyAccountManager(BaseUserManager):
#     def create_user(self,first_name,last_name,username,email,phone_number,password=None):
#         if not email:
#             raise ValueError("email is must enter")
#         if not username:
#             raise ValueError('user name is mandatory')
#         user = self.model(
#             email=self.normalize_email(email),
#             username=username,
#             first_name=first_name,
#             last_name=last_name,
#             phone_number=phone_number
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self,first_name,last_name,email,username,password):
#         user = self.create_user(
#             email=self.normalize_email(email),
#             username=username,
#             password=password,
#             first_name=first_name,
#             last_name=last_name,
#         )
#         is_admin = models.BooleanField(default=True)
#         is_staff = models.BooleanField(default=True)
#         is_active = models.BooleanField(default=True)
#         is_superadmin = models.BooleanField(default=True)
#         user.save(using=self._db)
#         return user
         
class Account(AbstractUser):
    first_name=models.CharField(max_length=60)
    last_name = models.CharField(max_length=70)
    username = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=100)
    email=models.EmailField(max_length=200,unique=True)
    phone_number = models.CharField(max_length=90, unique=True)
    # date=models.IntegerField(blank=True)


    #required

    date_joined=models.DateTimeField(auto_now_add=True)
    last_login =models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)


    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email','first_name','last_name']

    # objects=MyAccountManager()

    def __str__(self):
        return self.email
    # def has_perm(self,perm,obj=None):
    #     return self.is_admin
    # def has_module_perm(self,add_label):
    #     return True


class UserAddress(models.Model):
    user=models.ForeignKey(Account,on_delete=models.CASCADE)  
    address_name=models.CharField(max_length=50,blank=True)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.IntegerField(max_length=10)
    email=models.EmailField(max_length=50)
    address_line1=models.CharField(max_length=50)
    address_line2=models.CharField(max_length=50,blank=True)
    pin = models.IntegerField(max_length=6)
    
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)  


    def __str__(self):
        return self.first_name

class UserPropic(models.Model):
    user=models.OneToOneField(Account,on_delete=models.CASCADE) 
    pro_pic=models.ImageField(upload_to='pro_pics', null=True, blank=True)


    def image_url(self):
        try:
            url=self.pro_pic.url
        except:
            url='media/defaultProPic/defaultProPic.png'
        return url    

