from django.urls import path
from .views import CreateProductView, CompareView, DetailedProductView


urlpatterns = [
    path('create/', CreateProductView.as_view(), name='product-create'),
    path('compare/', CompareView.as_view(), name='compare-page'),
    path('<int:pk>/', DetailedProductView.as_view(), name='product-page')
]
