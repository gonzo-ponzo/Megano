from django.urls import path
from .views import cart_view, cart_add, cart_remove, cart_lower


urlpatterns = [
    path("cart/", cart_view, name="cart-page"),
    path("cart-add/<str:product_id>/<str:shop_id>", cart_add, name="cart-add"),
    path("cart-remove/<str:product_id>/<str:shop_id>", cart_remove, name="cart-remove"),
    path("cart-lower/<str:product_id>/<str:shop_id>", cart_lower, name="cart-lower"),
]
