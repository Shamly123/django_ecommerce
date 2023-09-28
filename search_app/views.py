from django.shortcuts import render, redirect
from product.models import Product
from django.db.models import Q


# Create your views here.


def searchresult(request):
    if request.method == "POST":
        query = request.POST.get("search")
        products = Product.objects.filter(Q(product_name__icontains=query))
        return render(request, "search.html", {"query": query, "products": products})
    return redirect("index")
