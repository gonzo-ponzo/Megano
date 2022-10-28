from django.views import View
from order.templatetags.cart import register
from shop.services import ShopDetail, ShopList
from django.shortcuts import render, redirect
from config.settings.base import COUNT_ELEMENTS_PAGINATOR_LIST_SHOPS
from django.core.paginator import Paginator



class ShopDetailView(View):
    """Страница магазина"""
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
        paginator = Paginator(object_list, COUNT_ELEMENTS_PAGINATOR_LIST_SHOPS)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(
            request,
            'shop/shop_list.html',
            {
            'object_list': page_obj,
            'full_object_list': object_list,
            'count_object_list': object_list.count()
            }
        )
