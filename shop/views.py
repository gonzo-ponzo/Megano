from django.views import View
from django.views.generic import ListView
from shop.services import ShopDetail
from django.shortcuts import render
from shop.models import Shop


class ShopDetailView(View):  # добавить проверку, если нет такого ID в бд, то отправлять на список магазинов
    """Страница продавца"""
    def get(self, request, *args, **kwargs):
        shop = ShopDetail(kwargs["pk"])
        shop_description = shop.get_shop_description
        top_products = shop.get_top_products
        shop_photos = shop.get_shop_photos
        return render(request, 'shop/shop.html', {
            'shop_description': shop_description,
            'top_products': top_products,
            'shop_photos': shop_photos
        })


class ShopListView(ListView):
    """Список магазинов"""
    model = Shop
    template_name = "shop/shop_list.html"
    paginate_by = 20
