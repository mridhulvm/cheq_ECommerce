from django.db import models

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=100,unique=True)
    is_available = models.BooleanField(default= True)
    
    cat_image = models.ImageField(upload_to = 'photos/categories/', blank = True )
    description = models.CharField(max_length=255,blank = True)

    def __str__(self):
        return self.category_name