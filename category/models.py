from django.db import models
from datetime import date


# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    is_available = models.BooleanField(default= True)

    offer_percentage  = models.IntegerField(null = True,blank = True)
 
    cat_image = models.ImageField(upload_to = 'photos/categories/', blank = True )
    description = models.CharField(max_length=255,blank = True)

    def __str__(self):
        return self.category_name

# Create your models here.
class CategoryOffer(models.Model):
    category=models.OneToOneField(Category,on_delete=models.CASCADE,blank = False)
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

