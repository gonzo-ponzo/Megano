from django.views import View
from shop.services import ShopDetail, ShopList
from django.shortcuts import render, redirect
# from django.conf import settings
from django.core.paginator import Paginator
from constance import config


class ShopDetailView(View):
    """Страница магазина"""

    def get(self, request, *args, **kwargs):
        """Получить данные по магазину: общая информация, ТОП продуктов, фотографии магазина"""
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
        """Получить 2 списка магазинов: с пагинацией и без, и количество магазинов"""
        object_list = ShopList().get_list_shops()
        paginator = Paginator(object_list, config.SHOPS_PER_PAGE)
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
