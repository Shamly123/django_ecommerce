from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import Address
from .models import Order, OrderItem, Coupon
import time, random, json
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# import paypalrestsdk
from django.conf import settings
from django.urls import reverse
import razorpay
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required


@login_required
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


@login_required
def cart_details(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            counter += cart_item.quantity
            offer = cart_item.product.get_offer_price() * cart_item.quantity
    except ObjectDoesNotExist:
        pass

    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        coupon = Coupon.objects.get(coupon_code=coupon_code)
        if coupon.min_price > total:
            messages.warning(
                request, f"minimum price should be greater than {coupon.min_price}"
            )
            return HttpResponseRedirect(request.path_info)
        elif cart.coupon:
            messages.warning(request, "coupon already applied")
            return HttpResponseRedirect(request.path_info)
        else:
            cart.coupon = coupon
            cart.save()
            messages.success(request, "coupon applied")
            return HttpResponseRedirect(request.path_info)

    if cart.coupon:
        order_total = total - cart.coupon.couon_price
    else:
        order_total = total

    order_total = float(order_total) - offer
    context = {
        "cart_items": cart_items,
        "total": total,
        "counter": counter,
        "order_total": round(order_total, 2),
        "cart": cart,
        "offer": offer,
    }

    return render(request, "cart.html", context)


@login_required
def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save(),
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)

        cart_item.save(),

    return redirect("cart_detail")


# def update_cart(request,):
@login_required
def update_cart(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_items = cart.cartItem.all()
    sub_total = 0
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data["id"]
        Qty = data["quantity"]
        cart_item = CartItem.objects.get(id=item_id)
        if int(Qty) > cart_item.product.stock:
            # messages.warning(request,'Out of stock')
            # return HttpResponseRedirect(request.path_info)

            error_message = "Out of Stock"  # Convert the error to a string
            return JsonResponse({"error": error_message}, status=400)

        cart_item.quantity = Qty
        cart_item.save()
        for cart_item in cart_items:
            sub_total += cart_item.product.price * cart_item.quantity
            offer = cart_item.product.get_offer_price() * cart_item.quantity
        if cart.coupon:
            total = sub_total - cart.coupon.couon_price
        else:
            total = sub_total
        order_total = float(total) - offer
        data = {
            "product_total": cart_item.sub_total(),
            "sub_total": sub_total,
            "offer": offer,
            "order_total": round(order_total, 2),
        }
    return JsonResponse(data)


@login_required
def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    else:
        cart_item.delete()
    return redirect("cart_detail")


@login_required
def full_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect("cart_detail")


@login_required
def checkout(request, total=0, counter=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            counter += cart_item.quantity
            offer = cart_item.product.get_offer_price() * cart_item.quantity

    except ObjectDoesNotExist:
        pass
    timestamp = int(time.time())
    random_number = random.randint(1000, 9999)
    order_number = f"ORD-{timestamp}-{random_number}"

    if cart.coupon:
        order_total = total - cart.coupon.couon_price
        coupon_price = cart.coupon.couon_price

    else:
        order_total = total
        coupon_price = 0

    order_total = float(order_total) - offer

    order = Order(
        user=request.user,
        order_number=order_number,
        subtotal=total,
        order_total=order_total,
        coupon_price=coupon_price,
        offer=offer,
    )
    order.save()
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
        )
    request.session["order_uid"] = str(order.uid)
    addresses = Address.objects.filter(user=request.user)
    context = {
        "cart_items": cart_items,
        "addresses": addresses,
        "total": total,
        "counter": counter,
        "order": order,
        "user": request.user,
        "cart": cart,
        "offer": offer,
    }
    return render(request, "checkout.html", context)


@login_required
def order_detail(request):
    order_uid = request.session["order_uid"]
    order = Order.objects.get(uid=order_uid)
    return render(request, "order-placed.html", {"order": order})


@login_required
def Cash_On_Delivery(request):
    total = 0
    selected_address_id = request.GET.get("selected_address")

    address = Address.objects.get(uid=selected_address_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
    except ObjectDoesNotExist:
        pass
    order_uid = request.session["order_uid"]
    order = Order.objects.get(uid=order_uid)
    order.status = "Order placed"
    order.is_orderd = True
    order.address = address
    order.method = "COD"
    order.save()
    for item in cart_items:
        item.product.stock -= item.quantity
        item.product.save()

    cart.delete()

    return redirect("order_detail")


# # for proceed to button in order pending
# def proceed_to_pay(request,order_id):
#     order = Order.objects.get(uid=order_id)
#     user = request.user
#     address = Address.objects.filter(user = user)


#     return (render(request,'checkout.html',dict(cart_items=order.order_item.all(),addresses=address,total=order.order_total, order=order,user=user)))


@login_required
def generate_pdf(request, order_id):
    # Fetch the order and its associated order_products
    order = get_object_or_404(Order, uid=order_id)
    order_products = OrderItem.objects.filter(order=order)

    total_price = sum(order_product.product.price for order_product in order_products)

    # Load the PDF template
    template_path = "invoice.html"
    template = get_template(template_path)

    # Prepare the template context
    context = {
        "order": order,
        "order_products": order_products,
        "total_price": total_price,
    }

    # Render the template to HTML
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="invoice_{order.order_number}.pdf"'

    # Generate the PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Check if PDF generation was successful
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response


# payment
@login_required
def payment(request):
    body = json.loads(request.body)
    OrdID = body["OrdID"]
    pid = body["PayID"]
    address_Id = body["address_Id"]
    order = order_placed(request, address_Id)

    order.is_orderd = True
    order.status = "Order Placed"
    order.payment_id = pid
    order.method = "Razor Pay"
    order.save()

    # cartItems to order item

    cart = Cart.objects.get(cart_id=_cart_id(request))

    cartItems = CartItem.objects.filter(cart=cart, active=True)
    for item in cartItems:
        item.product.stock -= item.quantity
        item.product.save()
    cart.delete()

    data = {"order_number": OrdID, "transID": pid}

    return JsonResponse(data)


@login_required
def order_placed(request, address_id):
    total = 0
    selected_address_id = address_id
    address = Address.objects.get(uid=selected_address_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
    except ObjectDoesNotExist as e:
        print(e)

    order_uid = request.session["order_uid"]
    order = Order.objects.get(uid=order_uid)
    order.address = address
    order.save()

    return order
