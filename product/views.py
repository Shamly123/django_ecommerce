from django.http import HttpResponse

from django.shortcuts import render,redirect
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from product.models import Product,Wishlist,Category
from django.http import JsonResponse
import json




# Create your views here.


def get_products(request,slug):
    product = Product.objects.get(slug=slug)
    offer = product.get_offer_price()
    if offer:
        offer_price = float(product.price) - offer
    else:
        offer_price = 0
    context={
        'product':product,
        'offer_price':round(offer_price,2)
        }
    return render(request,"prodemo.html",context)


def shop(request):
    if request.GET.get('c_id'):
        product = Product.objects.filter(category__category_name = request.GET.get('c_id'))
        category_name = request.GET.get('c_id')
        
    else:
        product = Product.objects.all()
        category_name = "all"
    
    category = Category.objects.all()
    paginator = Paginator(product, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'product': page_obj,
        'category':category,
        'category_name' : category_name
        
        }
    
    return render(request,"shop.html",context)


def wishlist(request):
    products = Wishlist.objects.filter(user = request.user)
    return render(request,'wishlist.html',{'products':products})

def add_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')

        products = Product.objects.get(id = product_id)
        Wishlist.objects.create(product = products,user = request.user)
        return JsonResponse({'success': True})

    
    return JsonResponse({'success': False})

    
def remove_wishlist(request,wishlist_id):
    wishlist = Wishlist.objects.get(uid = wishlist_id)
    wishlist.delete()
    
    return redirect('wishlist')