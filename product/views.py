from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render, get_object_or_404
from product.forms import ProductForm, ReviewForm
from product.models import Product, ProductView, ProductCategory
from promotion.services import BannerMain
from .services import ReviewForItem
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, DetailView, CreateView, ListView
from .utils import (
    get_main_pic,
    get_secondary_pics,
    get_min_price,
    get_top_price,
    get_discount,
    get_description,
    get_property_dict,
    get_offer_list,
)


class CreateProductView(CreateView):
    model = Product
    form_class = ProductForm


class MainPage(TemplateView):
    template_name = "product/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["banners"] = BannerMain.get_cache_banners()
        return context


class CompareView(TemplateView):
    template_name = "product/compare.html"


class CatalogView(ListView):
    # model = Product
    template_name = 'product/catalog.html'
    context_objects_name = 'product_list'

    def get_queryset(self):

        category = self.kwargs.get('category', None)

        queryset = Product.objects.all().prefetch_related('productimage_set')
        queryset = queryset.select_related('category')
        if category:
            category = get_object_or_404(ProductCategory, slug=category)
            queryset = queryset.filter(category__in=category.get_descendants(include_self=True))
        return queryset

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["list"] = Product.objects.all()
    #     return context


class DetailedProductView(DetailView):
    model = Product
    template_name = "product/product.html"
    TIMEOUT = settings.SESSION_COOKIE_AGE
    _paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(DetailedProductView, self).get_context_data(**kwargs)
        context["main_pic"] = cache.get_or_set(f"main_pic{self.object.id}", get_main_pic(self.object))
        context["pics"] = cache.get_or_set(f"pics{self.object.id}", get_secondary_pics(self.object))
        context["low_price"] = cache.get_or_set(f"low_price{self.object.id}", get_min_price(self.object))
        context["top_price"] = cache.get_or_set(f"top_price{self.object.id}", get_top_price(self.object))
        context["discount"] = cache.get_or_set(f"discount{self.object.id}", get_discount(self.object))
        context["product_description"] = cache.get_or_set(
            f"product_description{self.object.id}", get_description(self.object)
        )
        context["property_dict"] = cache.get_or_set(f"property_dict{self.object.id}", get_property_dict(self.object))
        context["offer_list"] = cache.get_or_set(f"offer_list{self.object.id}", get_offer_list(self.object))

        reviews = ReviewForItem(self.object)
        stars_order_by = reviews.get_stars_order_by()
        paginator = Paginator(reviews.get_reviews_product(), self._paginate_by)
        page_obj = paginator.get_page(kwargs.get("page_number", 1))

        context["page_obj"] = page_obj
        context["count_reviews"] = reviews.get_count_reviews_product()
        context["stars_rating_users"] = stars_order_by
        context["stars_rating"] = stars_order_by[::-1]
        context["reviews_form"] = ReviewForm()

        if self.request.user.id:
            # предлагаю создавать просмотр на админа(id=1),
            # если пользователь не авторизован
            product_view = ProductView(product=self.object, user=self.request.user)
            product_view.save()
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        page_number = request.GET.get("page", 1)
        context = self.get_context_data(page_number=page_number, **kwargs)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = request.POST

        if "delete" in data:
            ReviewForItem.delete_review(data["review_id"])
            messages.success(request, _("Отзыв удален."))
        else:
            reviews_form = ReviewForm(data)

            if reviews_form.is_valid():
                review_data = reviews_form.cleaned_data
                review = ReviewForItem(self.object)
                review.add_review(user=request.user, **review_data)
                messages.success(request, _("Отзыв добавлен."))
            else:
                page_number = request.POST.get("page", 1)
                context = self.get_context_data(page_number=page_number, **kwargs)
                context["reviews_form"] = reviews_form
                messages.error(request, _("Отзыв не добавлен, проверьте корректность ввода."))
                return render(request, self.template_name, context=context)

        return redirect("product-page", self.object.pk)
