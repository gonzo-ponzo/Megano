from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from product.forms import ProductForm, ReviewForm
from product.models import Product
from promotion.services import BannerMain
from django.views.generic import TemplateView, DetailView, CreateView
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


class CompareView(TemplateView):
    template_name = 'product/compare.html'


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
            'main_pic', get_main_pic(self.object)
        )
        context['pics'] = cache.get_or_set(
            'pics', get_secondary_pics(self.object)
        )
        context['low_price'] = cache.get_or_set(
            'low_price', get_min_price(self.object)
        )
        context['top_price'] = cache.get_or_set(
            'top_price', get_top_price(self.object)
        )
        context['discount'] = cache.get_or_set(
            'discount', get_discount(self.object)
        )
        context['product_description'] = cache.get_or_set(
            'product_description', get_description(self.object)
        )
        context['property_dict'] = cache.get_or_set(
            'property_dict', get_property_dict(self.object)
        )
        context['offer_list'] = cache.get_or_set(
            'offer_list', get_offer_list(self.object)
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
