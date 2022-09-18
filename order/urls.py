from django.urls import path
from .views import cart_view, cart_add, cart_remove, cart_lower


urlpatterns = [
    path("cart/", cart_view, name="cart-page"),
    path("cart-add/<int:pk>/<int:shop_id>", cart_add, name="cart-add"),
    path("cart-remove/<int:pk>/<int:shop_id>", cart_remove, name="cart-remove"),
    path("cart-lower/<int:pk>/<int:shop_id>", cart_lower, name="cart-lower"),
]
