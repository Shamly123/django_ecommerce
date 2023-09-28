from django.contrib import admin
from .models import Category, Product, Product_Image,Offer


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name','slug']
    prepopulated_fields = {'slug':('category_name',)}
admin.site.register(Category,CategoryAdmin)



class Product_ImageAdmin(admin.StackedInline):
    model = Product_Image

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'stock', 'available']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('product_name',)}
    list_per_page = 20
    inlines = [Product_ImageAdmin]

admin.site.register(Product, ProductAdmin)
admin.site.register(Offer)
