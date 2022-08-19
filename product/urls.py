from django.urls import path
from .views import CreateProductView


urlpatterns = [
    path('create/', CreateProductView.as_view(), name='product-create'),
]
