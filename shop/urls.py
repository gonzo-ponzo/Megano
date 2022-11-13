from django.urls import path
from shop.views import ShopDetailView, ShopListView

urlpatterns = [
    path("<int:pk>", ShopDetailView.as_view(), name="shop-detail"),
    path("", ShopListView.as_view(), name="shop-list"),
]
