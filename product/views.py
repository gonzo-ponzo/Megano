from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from product.forms import ProductForm, ReviewForm
from product.models import Product
from promotion.services import BannerMain
from .services import ReviewForItem
from django.views.generic import TemplateView, DetailView, CreateView
from .utils import get_main_pic, get_secondary_pics, get_min_price, \
    get_top_price, get_discount, get_description, \
    get_property_dict, get_offer_list


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

        reviews = ReviewForItem(self.object)
        stars_order_by = reviews.get_stars_order_by()
        context["reviews"] = reviews.get_reviews()
        context["count_reviews"] = reviews.get_count_reviews()
        context["stars_rating_users"] = stars_order_by
        context["stars_rating"] = stars_order_by[::-1]
        context["reviews_form"] = ReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        reviews_form = ReviewForm(request.POST)

        if reviews_form.is_valid():
            data = reviews_form.cleaned_data
            user = request.user
            review = ReviewForItem(self.object)
            review.add_review(user=user, **data)
            return redirect("product-page", self.object.pk)

        context = self.get_context_data()
        context["reviews_form"] = reviews_form
        return render(request, "product/product.html", context=context)
