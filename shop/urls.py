from django.urls import path
from shop.views import ShopListView

urlpatterns = [
    path('', ShopListView.as_view(), name='product-create'),
]