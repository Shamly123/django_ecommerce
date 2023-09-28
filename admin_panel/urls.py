from django.urls import path


from . import views
urlpatterns = [
        path('', views.index,name ='indexes'),
        path('admin-login/',views.admin_login,name='admin_login'),
        path('admin_logout/',views.admin_logout,name='admin_logout'),
        path('user_management/',views.user_view,name='user_view'),
        path('user_search/', views.user_search, name='user_search'),

        path('user_status/<int:user_id>/',views.user_status,name='user_status'),
        path('category_management/',views.category,name='category_management'),
        path('add_category/',views.add_category,name='add_category'),
        path('edit_category/<uuid:cat_id>/',views.edit_category,name='edit_category'),
        path('delete-category/<uuid:cat_id>/',views.delete_category,name='delete_category'),
        path('product-management/',views.product,name='product_management'),
        path('search_product/', views.product_search, name='product_search'),
        path('edit_product/<int:pro_id>/',views.edit_product,name='edit_product'),
        path('delete-product/<int:pro_id>/',views.delete_product,name='delete_product'),
        path('add-product/',views.add_product,name='add_product'),
        path('product-image/<int:pro_id>/', views.product_image, name='product_image'),
        path("addimage/<int:uid>", views.addimage, name="addimage"),
        path('image_delete/<int:pro_id>/', views.delete_image, name='image_delete'),
        path('order-management/',views.Orders,name='order_management'),
        path('edit_order_status/<uuid:od_id>/',views.edit_order_status,name='edit_order_status'),
        path('order_details/<uuid:order_uid>/', views.order_details, name='order_details'),
        path("sales_report/", views.sales_report, name="sales_report"),
        path('coupon/',views.coupon,name='coupon_management'),
        path('add_coupon/',views.add_coupon,name='add_coupon'),
        path('edit_coupon/<uuid:c_id>/',views.edit_coupon,name='edit_coupon'),
        path('delete_coupon/<uuid:c_id>/',views.delete_coupon,name='delete_coupon'),
        path('offer/',views.offer,name='offer_management'),
        path('add_offer/',views.add_offer,name='add_offer'),
        path('edit_offer/<uuid:o_id>/',views.edit_offer,name='edit_offer'),
        path('delete_offer/<uuid:o_id>/',views.delete_offer,name='delete_offer'),
        


]