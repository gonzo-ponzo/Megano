from django.urls import path
from .views import (
    cart_view,
    cart_add,
    cart_remove,
    cart_lower,
    cart_clear,
    CreateOrderView,
    OrderHistoryListView,
    OrderHistoryDetailView,
)

urlpatterns = [
    path("cart/", cart_view, name="cart-page"),
    path("cart-add/<str:product_id>/<str:shop_id>/", cart_add, name="cart-add"),
    path("cart-remove/<str:product_id>/<str:shop_id>/", cart_remove, name="cart-remove"),
    path("cart-lower/<str:product_id>/<str:shop_id>/", cart_lower, name="cart-lower"),
    path("cart-clear/", cart_clear, name="cart-clear"),
    path("create/", CreateOrderView.as_view(), name="create-order"),
    path("history/", OrderHistoryListView.as_view(), name="history-orders"),
    path("history/<int:pk>", OrderHistoryDetailView.as_view(), name="history-order-detail"),
]
