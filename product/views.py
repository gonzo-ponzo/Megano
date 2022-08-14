from django.views.generic import CreateView

from product.forms import ProductForm
from product.models import Product


class CreateProductView(CreateView):
    model = Product
    form_class = ProductForm
