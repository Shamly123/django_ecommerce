from django.urls import path
# from .views import InvoicePDFView


from . import views
urlpatterns=[
    path('add/<int:product_id>/',views.add_cart,name='add_cart'),
    path('',views.cart_details,name='cart_detail'),
    path('remove/<int:product_id>/',views.cart_remove,name='cart_remove'),
    path('full_remove/<int:product_id>/',views.full_remove,name='full_remove'),
    path('checkout/',views.checkout,name='checkout'),
    # path('proceed_to_pay/<uuid:order_id>/',views.proceed_to_pay,name='proceed_to_pay'),
    path('order/', views.order_detail, name='order_detail'),
    path('Cash_On_Delivery/', views.Cash_On_Delivery, name="Cash_On_Delivery"),
    path('download_invoice/<uuid:order_id>/', views.generate_pdf, name='download_invoice'),
    path('update_cart/', views.update_cart, name="update_cart"),
    path('payment/',views.payment, name="payment"),
   
]
    


