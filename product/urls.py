from django.urls import path
from .views import CreateProductView, CatalogView, CompareView


urlpatterns = [
    path('create/', CreateProductView.as_view(), name='product-create'),
    path('catalog/', CatalogView.as_view(), name='catalog-page'),
    path('compare/', CompareView.as_view(), name='compare-page'),
]
