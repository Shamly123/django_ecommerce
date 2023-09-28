from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from product.models import Category, Product, Product_Image, Offer
from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Profile
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from cart.models import Order, Coupon
from .forms import ImageForm
from django.db.models import Q
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime, timedelta
import json
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4


# Create your views here.
# admin dashboard
def index(request):
    if not request.user.is_superuser:
        return redirect("admin_login")
    # sales report
    selected_value = request.GET.get("selected_value")
    current_date = timezone.now()
    current_month = current_date.month
    current_year = current_date.year
    current_week = current_date.isocalendar()[1]
    current_day = timezone.now().date()
    user_type = []
    revenue_year = Order.objects.filter(
        created_at__year=current_year, status="Delivered"
    ).aggregate(total=Sum("order_total"))["total"]

    revenue_month = (
        Order.objects.filter(
            created_at__year=current_year,
            created_at__month=current_month,
            status="Delivered",
        ).aggregate(total_price_sum=Sum("order_total"))["total_price_sum"]
        or 0
    )

    revenue_week = Order.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month,
        created_at__week=current_week,
        status="Delivered",
    ).aggregate(total_price_sum=Sum("order_total"))["total_price_sum"]

    revenue_day = Order.objects.filter(
        created_at__date=current_day, status="Delivered"
    ).aggregate(total_price_sum=Sum("order_total"))["total_price_sum"]

    gust_count = Order.objects.filter(user__isnull=True, is_orderd=True).count()

    user_type.append(gust_count)

    user_count = Order.objects.filter(user__isnull=False, is_orderd=True).count()
    user_type.append(user_count)

    if selected_value == "month":
        # for chart
        # Create a list to hold total prices for each month
        monthly_total_prices = []
        previous = []
        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        # Iterate through each month (from January to December)
        for month_number in range(1, 13):
            total_price_curr = (
                Order.objects.filter(
                    created_at__month=month_number,
                    status="Delivered",
                    created_at__year=current_year,
                ).aggregate(total_price_sum=Sum("order_total"))["total_price_sum"]
                or 0
            )

            total_price_pre = (
                Order.objects.filter(
                    created_at__month=month_number,
                    status="Delivered",
                    created_at__year=(current_year - 1),
                ).aggregate(total_price_sum=Sum("order_total"))["total_price_sum"]
                or 0
            )

            total_price_float_curr = float(total_price_curr)
            monthly_total_prices.append(total_price_float_curr / 10)

            total_price_float_pre = float(total_price_pre)
            previous.append(total_price_float_pre / 10)
        print(total_price_float_pre)
        data = {
            "current": monthly_total_prices,
            "previous": previous,
            "previousstr": "previous year",
            "currentstr": "current year",
            "revenue": revenue_year,
            "category": months,
        }
        return JsonResponse(data)

    if selected_value == "year":
        yearly_total_prices = []
        year = [(current_year - 10) + i for i in range(11)]

        for year_number in year:
            total_price_curr = (
                Order.objects.filter(
                    created_at__year=year_number,
                    status="Delivered",
                ).aggregate(total_price_sum=Sum("order_total"))["total_price_sum"]
                or 0
            )

            total_price_float_curr = float(total_price_curr)
            yearly_total_prices.append(total_price_float_curr / 10)

        data = {
            "current": yearly_total_prices,
            "previous": None,
            "previousstr": None,
            "currentstr": "current week",
            "revenue": revenue_month,
            "category": year,
        }
        return JsonResponse(data)

    current_date = datetime.now()
    start_date = current_date - timedelta(days=14)
    daily_total = []

    while start_date <= current_date:
        daily_total_price = (
            Order.objects.filter(
                created_at__date=start_date, status="Delivered"
            ).aggregate(total_price_sum=Sum("order_total"))["total_price_sum"]
            or 0
        )

        daily_total_price_float = float(daily_total_price)
        daily_total.append(daily_total_price_float)

        start_date += timedelta(days=1)

    month = current_date.strftime("%b")

    monthly = json.dumps(daily_total)
    total_order = Order.objects.filter(is_orderd=True).count()
    user_type_json = json.dumps(user_type)
    context = {
        "user_type": user_type_json,
        "total_order": total_order,
        "monthly": monthly,
        "revenue_month": round(revenue_month, 2),
        "current_month": month,
    }

    return render(request, "index_3.html", context)


# sales_get_report
def sales_report(request):
    if request.method == "POST":
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        format = request.POST["format"]
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                if start_date != end_date:
                    orders = Order.objects.filter(
                        status="Delivered", created_at__range=(start_date, end_date)
                    )
                else:
                    orders = Order.objects.filter(
                        status="Delivered", created_at__date=start_date
                    )

                # Rest of your code for generating reports

            except ValueError as e:
                # Handle invalid date input, e.g., display an error message to the user
                return HttpResponse(
                    "Invalid date input. Please use the format YYYY-MM-DD."
                )
        else:
            # Handle cases where start_date or end_date is not provided
            return HttpResponse("Both start_date and end_date are required.")

        if format == "pdf":
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="sales_report.pdf"'
            doc = SimpleDocTemplate(response, pagesize=A4)
            table_style = TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )

            data = [
                [
                    "Sl",
                    "Order Number",
                    "User Name",
                    "User Email",
                    "Shipping Address",
                    "Payment Method",
                    "Order Total",
                    "Created Date",
                ]
            ]
            counter = 1
            total = 0
            for order in orders:
                user_email = order.user.email if order.user else "Guest User"
                created_date = order.created_at.strftime("%d-%m-%Y %I:%M %p")
                data.append(
                    [
                        counter,
                        order.order_number,
                        order.user.first_name,
                        user_email,
                        order.address.city,
                        order.method,
                        # order.payment.payment_method,
                        order.order_total,
                        created_date,
                    ]
                )
                counter += 1
                total += order.order_total
            data.append([])
            data.append(["", "Total Amount", "", "", total])
            table = Table(data)
            table.setStyle(table_style)

            # Build the PDF document
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Sales Report", styles["Title"]))
            elements.append(table)

            doc.build(elements)

            return response

        if format == "excel":
            # output = io.BytesIO()
            wb = Workbook()
            ws = wb.active
            headers = [
                "Sl",
                "Order Number",
                "User Name",
                "User Email",
                "User Address",
                "Payment Method",
                "Order Total",
                "Created Date",
            ]
            ws.append(headers)

            counter = 1
            for order in orders:
                user_email = order.user.email if order.user else "Guest User"
                created_date = order.created_at.strftime("%d-%m-%Y %I:%M %p")
                row_data = [
                    counter,
                    order.order_number,
                    order.user.first_name,
                    user_email,
                    order.address.city,
                    order.method,
                    order.order_total,
                    created_date,
                ]
                ws.append(row_data)
                counter += 1

            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            # Create an HTTP response with the Excel file
            response = HttpResponse(
                output.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = 'attachment; filename="sales_report.xlsx"'

            return response


def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("indexes")
        return redirect("admin_login")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect("indexes")
        error = "invalid User"

        return render(request, "authentication-login.html", {"error_messege": error})

    return render(request, "authentication-login.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_login")


def not_superuser(user):
    return not user.is_superuser


def user_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    users = Profile.objects.filter(is_superuser=False)
    paginator = Paginator(users, 4)
    page_number = request.GET.get("page")
    user_obj = paginator.get_page(page_number)
    return render(request, "user-management.html", {"users": user_obj})


# user search
def user_search(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    query = request.GET.get("q")

    if query:
        users = Profile.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    else:
        users = []

    return render(request, "admin_user_search.html", {"users": users})


def user_status(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    user = Profile.objects.get(id=user_id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()
    return redirect("user_view")


def category(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    categories = Category.objects.all()
    offers = Offer.objects.all()
    return render(
        request,
        "category-management.html",
        {"categories": categories, "offers": offers},
    )


def add_category(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    if request.method == "POST":
        category_name = request.POST.get("category_name")
        category_obj = Category.objects.create(category_name=category_name)
        category_obj.save()

    return redirect("category_management")


def edit_category(request, cat_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    if request.method == "POST":
        new_category_name = request.POST.get("category_name")
        category = Category.objects.get(uid=cat_id)
        category.category_name = new_category_name
        category.save()
    return redirect("category_management")


def delete_category(request, cat_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    category = Category.objects.get(uid=cat_id)
    category.delete()
    return redirect("category_management")


def product(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    products = Product.objects.all()
    category = Category.objects.all()
    offers = Offer.objects.all()

    category_filter = request.GET.get("category")
    if category_filter:
        products = products.filter(category__uid=category_filter)

    sort_option = request.GET.get("sort")
    if sort_option == "name_asc":
        products = products.order_by("product_name")
    elif sort_option == "name_desc":
        products = products.order_by(
            "-product_name"
        )  # Use '-' to indicate descending order
    elif sort_option == "price_asc":
        products = products.order_by("price")
    elif sort_option == "price_desc":
        products = products.order_by("-price")

    context = {"products": products, "categories": category, "offers": offers}
    return render(request, "product-management.html", context)


# search products
def product_search(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    query = request.GET.get("q")

    if query:
        products = Product.objects.filter(product_name__icontains=query)
    else:
        products = []

    return render(request, "admin_product_search_result.html", {"products": products})


def edit_product(request, pro_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    if request.method == "POST":
        product_name = request.POST.get("product_name")
        category_id = request.POST.get("category")
        offer_id = request.POST.get("offer")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")

        products = Product.objects.get(id=pro_id)
        category = Category.objects.get(uid=category_id)
        offer = Offer.objects.get(uid=offer_id)

        products.product_name = product_name
        products.category = category
        products.offer = offer
        products.description = description
        products.price = price
        products.stock = stock

        category.save()
        offer.save()
        products.save()
    return redirect("product_management")


def delete_product(request, pro_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    products = Product.objects.get(id=pro_id)

    products.delete()

    return redirect("product_management")


def add_product(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    if request.method == "POST":
        product_name = request.POST.get("product_name")
        category_id = request.POST.get("category")
        offer_id = request.POST.get("offer")
        description = request.POST.get("description")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category = Category.objects.get(uid=category_id)
        offer = Offer.objects.get(uid=offer_id)
        category.save()
        offer.save()
        product_obj = Product.objects.create(
            product_name=product_name,
            category=category,
            offer=offer,
            description=description,
            price=price,
            stock=stock,
        )

        product_obj.save()

    return redirect("product_management")


# def product_image(request,pro_id):
#     if not request.user.is_authenticated or not request.user.is_superuser:
#         return redirect('admin_login')
#     products = Product.objects.get(id=pro_id)
#     product_images=products.product_images.all()

#     return render(request, 'product-image.html',{'pro':product_images})


def product_image(request, pro_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    product = Product.objects.get(id=pro_id)
    product_images = product.product_images.all()

    if request.method == "POST":
        image = request.FILES.get(
            "image"
        )  # Assuming you're uploading the image via a form

        if image:
            product_image = Product_Image.objects.create(product=product, image=image)
            product_image.save()

    return render(
        request, "product-image.html", {"pro": product_images, "product": product}
    )


def addimage(request, uid):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        product = Product.objects.get(id=uid)

        if form.is_valid():
            image_instance = form.save(commit=False)
            image_instance.product = product
            image_instance.save()

            return JsonResponse({"message": "works", "img_id": uid})

        else:
            print("Form is not valid:", form.errors)

    else:
        form = ImageForm()

    context = {"form": form, "img_id": uid}
    return render(request, "add-image.html", context)


def delete_image(request, pro_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    try:
        product_image = Product_Image.objects.get(id=pro_id)
        product_id = product_image.product.id  # Get the associated product's ID
        product_image.delete()
    except ObjectDoesNotExist:
        pass

    return redirect("product_image", pro_id=product_id)  # Use pro_id here


def Orders(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    orders = Order.objects.all()
    return render(request, "order-management.html", {"orders": orders})


def edit_order_status(request, od_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    if request.method == "POST":
        new_status = request.POST.get("order_status")
        orders = Order.objects.get(uid=od_id)
        orders.status = new_status
        orders.save()
    return redirect("order_management")


# order details
def order_details(request, order_uid):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    order = get_object_or_404(Order, uid=order_uid)

    # Retrieve related order items and address
    order_items = order.order_item.all()

    return render(
        request,
        "admin_order_details.html",
        {"order": order, "order_items": order_items},
    )


def coupon(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    coupons = Coupon.objects.all()
    return render(request, "coupon.html", {"coupons": coupons})


def add_coupon(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        coupon_price = request.POST.get("coupon_price")
        min_price = request.POST.get("min_price")
        coupon_obj = Coupon.objects.create(
            coupon_code=coupon_code, couon_price=coupon_price, min_price=min_price
        )
        coupon_obj.save()

    return redirect("coupon_management")


def edit_coupon(request, c_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        coupon_price = request.POST.get("coupon_price")
        min_price = request.POST.get("min_price")

        coupon = Coupon.objects.get(uid=c_id)
        coupon.coupon_code = coupon_code
        coupon.couon_price = coupon_price
        coupon.min_price = min_price
        coupon.save()
    return redirect("coupon_management")


def delete_coupon(request, c_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    coupon = Coupon.objects.get(uid=c_id)
    coupon.delete()
    return redirect("coupon_management")


def offer(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    offers = Offer.objects.all()
    return render(request, "offer-management.html", {"offers": offers})


def add_offer(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    if request.method == "POST":
        name = request.POST.get("offer")
        percentage = request.POST.get("percentage")
        offer_obj = Offer.objects.create(name=name, percentage=percentage)
        offer_obj.save()

    return redirect("offer_management")


def edit_offer(request, o_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    if request.method == "POST":
        name = request.POST.get("offer")
        percentage = request.POST.get("percentage")

        offer = Offer.objects.get(uid=o_id)
        offer.name = name
        offer.percentage = percentage
        offer.save()
    return redirect("offer_management")


def delete_offer(request, o_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    offer = Offer.objects.get(uid=o_id)
    offer.delete()
    return redirect("offer_management")
