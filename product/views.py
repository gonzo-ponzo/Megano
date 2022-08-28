from django.views.generic import CreateView
from product.forms import ProductForm
from product.models import Product
from django.views.generic import TemplateView


class CreateProductView(CreateView):
    model = Product
    form_class = ProductForm


class MainPage(TemplateView):
    template_name = 'index.html'


class LoginView(TemplateView):
    template_name = 'login.html'


class CompareView(TemplateView):
    template_name = 'compare.html'


class CatalogView(TemplateView):
    model = Product
    template_name = 'catalog.html'
    context_objects_name = 'product_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list'] = Product.objects.all()
        return context
