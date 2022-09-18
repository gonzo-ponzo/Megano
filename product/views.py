from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views import View
from product.forms import ProductForm, ReviewForm
from product.models import Product
from promotion.services import BannerMain
from django.views.generic import TemplateView, DetailView, CreateView

from .services import ComparisonList
from .utils import get_main_pic, get_secondary_pics, get_min_price, \
    get_top_price, get_discount, get_description, \
    get_property_dict, get_offer_list, get_review


class CreateProductView(CreateView):
    model = Product
    form_class = ProductForm


class MainPage(TemplateView):
    template_name = 'product/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["banners"] = BannerMain.get_cache_banners()
        return context


class CompareView(View):

    def get(self, request, *args, **kwargs):
        compare_list = ComparisonList().get_compare_list()
        return render(request, 'product/compare.html', {'compare_list': compare_list})


class CompareAdd(View):

    def get(self, request, *args, **kwargs):
        ComparisonList().add_item(kwargs['pk'])
        return render(request, 'product/compare_change.html', {'message': 'объект добавлен'})


class CompareRemove(View):

    def get(self, request, *args, **kwargs):
        ComparisonList().remove_item(kwargs['pk'])
        return render(request, 'product/compare_change.html', {'message': 'объект удален'})


class CompareClear(View):

    def get(self, request, *args, **kwargs):
        ComparisonList().remove_item(kwargs['pk'])
        return render(request, 'product/compare_change.html', {'message': 'список очищен'})

class CatalogView(TemplateView):
    model = Product
    template_name = 'product/catalog.html'
    context_objects_name = 'product_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list"] = Product.objects.all()
        return context


class ProductView(DetailView):
    model = Product
    template_name = 'product/product.html'
    TIMEOUT = settings.SESSION_COOKIE_AGE

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        context['main_pic'] = cache.get_or_set(
            f'main_pic{self.object.id}', get_main_pic(self.object)
        )
        context['pics'] = cache.get_or_set(
            f'pics{self.object.id}', get_secondary_pics(self.object)
        )
        context['low_price'] = cache.get_or_set(
            f'low_price{self.object.id}', get_min_price(self.object)
        )
        context['top_price'] = cache.get_or_set(
            f'top_price{self.object.id}', get_top_price(self.object)
        )
        context['discount'] = cache.get_or_set(
            f'discount{self.object.id}', get_discount(self.object)
        )
        context['product_description'] = cache.get_or_set(
            f'product_description{self.object.id}', get_description(self.object)
        )
        context['property_dict'] = cache.get_or_set(
            f'property_dict{self.object.id}', get_property_dict(self.object)
        )
        context['offer_list'] = cache.get_or_set(
            f'offer_list{self.object.id}', get_offer_list(self.object)
        )
        context['reviews'] = get_review(self.object)
        context['form'] = ReviewForm
        return context

    def post(self, request, pk, *args, **kwargs):
        form = ReviewForm(request.POST)
        new_review = form.save(commit=False)
        new_review.product = Product.objects.get(id=pk)
        new_review.user = request.user
        new_review.save()
        return redirect(request.META.get('HTTP_REFERER',
                                         'redirect_if_referer_not_found'))
