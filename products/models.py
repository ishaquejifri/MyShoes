from django.db import models
from category.models import Category
from django.db.models import Avg,Count
from PIL import Image

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()
    is_listed = models.BooleanField(default=True) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    offer_price = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)

    @property
    def discount_percentage(self): 
        if self.offer_price and self.base_price > 0:
            return int(((self.base_price - self.offer_price) / self.base_price) * 100 )
        return 0

    def __str__(self):
        return self.product_name
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')

    def __str__(self):
        return self.product.product_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        width, height = img.size
        min_dim = min(width,height)

        left = (width - min_dim)
        top = (height - min_dim)
        right = (width + min_dim)
        bottom = (width + min_dim)

        img = img.crop((left,top,right,bottom))
        img = img.resize((500, 500))

        img.save(self.image.path)

# this is the standarized model
# SIZE_CHOICES = [

#     ('7','7'),
#     ('8','8'),
#     ('9','9'),
#     ('10','10'),
    
# ]

# COLOR_CHOICES = [

#     ('Black','Black'),
#     ('Blue','Blue'),
#     ('White','White'),
#     ('Brown','Brown'),
#     ('Green','Green'),
#     ('Orange','Orange')
# ]

class ProductVariant(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='variants')
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.product_name} - {self.size} - {self.color}"



    

