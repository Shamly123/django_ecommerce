from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_page, name="login_page"),
    path("register/", views.register_page, name="register"),
    path("user_logout/", views.user_logout, name="user_logout"),
    path("user_profile/", views.user_profile, name="user_profile"),
    path("user_address/", views.address_view, name="user_address"),
    path("add_address/", views.add_address, name="add_address"),
    path("edit_address/<uuid:ad_id>/", views.edit_address, name="edit_address"),
    path("delete_address/<uuid:add_id>/", views.delete_address, name="delete_address"),
    path("user_details/", views.user_detail, name="user_detail"),
    path(
        "edit_user-details/<int:user_id>/",
        views.edit_user_detail,
        name="edit_user_detail",
    ),
    path(
        "change_profile_picture/<int:user_id>/",
        views.change_profile_picture,
        name="change_picture",
    ),
    path(
        "reset_password/", views.ResetPassword, name="reset_password"
    ),  # changepassword function
    path("change_password/", views.change_password, name="change_password"),
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    path(
        "resetPassword/", views.reset_password, name="resetPassword"
    ),  # reset password for forgot password
    path("userorders/", views.user_orders, name="userOrders"),
    path(
        "user_single_order/<uuid:order_id>/",
        views.user_single_order,
        name="user_single_order",
    ),  # order details
    path("cancel_order/<uuid:order_id>/", views.cancel_order, name="cancel_order"),
    path("return_order/<uuid:order_id>/", views.return_order, name="return_order"),
]
