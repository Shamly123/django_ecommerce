from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from accounts.models import Profile




class Offer(BaseModel):
    name = models.CharField(max_length=50)
    percentage = models.BigIntegerField()

    def __str__(self) -> str:
        return self.name


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, unique=True,null=True,blank=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, blank=True, null=True)


    class Meta:
        ordering=('category_name',)
        verbose_name='category'
        verbose_name_plural='categories'

    def save(self,*args,**kwargs):
        self.slug=slugify(self.category_name)
        super(Category,self).save(*args,**kwargs)


    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category,on_delete=models.CASCADE, related_name = "products")
    price=models.DecimalField(max_digits=10,decimal_places=2)
    description = models.CharField(max_length=300)
    slug = models.SlugField(max_length=250, unique=True,null=True,blank=True)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ('product_name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def save(self,*args,**kwargs):
        self.slug=slugify(self.product_name)
        super(Product,self).save(*args,**kwargs)


    def __str__(self):
        return '{}'.format(self.product_name)
    
    def get_offer_price(self):
        p_price = 0
        c_price = 0
        if self.offer:
            p_price = float(self.price) * float(self.offer.percentage / 100)

        if self.category.offer:
            c_price = float(self.price) * float(self.category.offer.percentage / 100)

        if p_price and c_price:
            price = max(p_price, c_price)
        elif p_price and not c_price:
            price = p_price
        elif not p_price and c_price:
            price = c_price
        else:
            price = 0

        return price



class Product_Image(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="product_images")
    image = models.ImageField(upload_to= "product")



class Wishlist(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile,on_delete=models.CASCADE, null=True)
    
    
    
