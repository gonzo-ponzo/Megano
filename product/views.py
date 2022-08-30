from django.shortcuts import render
from django.views.generic import CreateView
from product.forms import ProductForm
from product.models import Product
from django.views.generic import TemplateView
from .services import GetProduct

GetProduct = GetProduct()


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

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['list'] = Product.objects.all()
    #     return context

    def get(self, request, *args, **kwargs):
        category_tree = [request.GET.get(f'level{i}', None)
                         for i in range(1, len(request.GET) + 1)]

        products = GetProduct.get_product_list(category_tree=category_tree)

        return render(request=request,
                      template_name=self.template_name,
                      context={'products': products})
