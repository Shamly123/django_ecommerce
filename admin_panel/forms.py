from django import forms
from product.models import Product_Image


class ImageForm(forms.ModelForm):
    class Meta:
        model = Product_Image
        fields = ("image",)