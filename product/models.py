from django.db import models
from django.urls import reverse
from category.models import Category


# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique= True)
    slug         = models.CharField(max_length = 200, unique= True)
    description  = models.TextField(max_length = 500, blank = True)
    
    price        = models.IntegerField()
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