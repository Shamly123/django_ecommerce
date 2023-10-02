from django.shortcuts import render
from product.models import Product


# Create your views here.


def index(request):
    context = {"products": Product.objects.all()[:6]}
    return render(request, "index_2.html", context)


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


