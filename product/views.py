from django.views.generic import CreateView
from django.shortcuts import render  # noqa: F401
from product.forms import ProductForm
from product.models import Product
from django.views.generic import TemplateView


class CreateProductView(CreateView):
    model = Product
    form_class = ProductForm


class MainPage(TemplateView):
    template_name = "index.html"
