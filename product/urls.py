from django.conf.urls.static import static
from django.urls import path


from . import views

urlpatterns = [
    path("product/<slug>/", views.get_products, name="get_products"),
    path("shop/", views.shop, name="shopview"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("add_wishlist/", views.add_wishlist, name="add_to_wishlist"),
    path(
        "remove_wishlist/<uuid:wishlist_id>/",
        views.remove_wishlist,
        name="remove_wishlist",
    ),
]
