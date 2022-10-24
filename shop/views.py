from django.views import View
from shop.models import Shop
from shop.services import ShopDetail, ShopList
from django.shortcuts import render, redirect
from product.services import FilterProductsResult
from config.settings.base import COUNT_ELEMENTS_BEST_OFFER_SHOP


class ShopDetailView(View):
    """Страница продавца"""
    def get(self, request, *args, **kwargs):
        shop = ShopDetail(kwargs["pk"])
        if shop.get_shop_status():
            shop_description = shop.get_shop_description()
            top_products = shop.get_top_products()
            shop_photos = shop.get_shop_photos()
            return render(request, 'shop/shop.html', {
                'shop_description': shop_description,
                'top_products': top_products,
                'shop_photos': shop_photos
            })
        return redirect('shop-list')


class ShopListView(View):
    """Список магазинов"""
    def get(self, request, *args, **kwargs):
        object_list = ShopList().get_list_shops()
        return render(request, 'shop/shop_list.html', {'object_list': object_list})
