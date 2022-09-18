import random

from django.conf import settings
from django.core.cache import cache

from .models import Banner


class BannerMain:
    """Баннеры на главной странице"""

    _count = 3

    @classmethod
    def get_active_banners(cls):
        """Получить баннеры"""
        return Banner.objects.filter(is_active=True).only("pk", "name", "description", "product", "image")

    @classmethod
    def _get_count_active_banners(cls):
        """Получить нужное количество баннеров"""
        banners = cls.get_active_banners()
        count_banners = len(banners)
        if count_banners >= cls._count:
            count_banners = cls._count
        return random.sample(list(banners), count_banners)

    @classmethod
    def get_cache_banners(cls):
        """Получить кэш"""
        return cache.get_or_set(
            settings.CACHE_KEY_BANNER,
            cls._get_count_active_banners,
            settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_BANNER),
        )


class LimitedProduct:
    """Ограниченный товар"""

    def get_limited_product(self):
        """Получить ограниченный товар"""
        pass

    def get_timer(self):
        """Получить таймер на ограниченный товар"""
        pass


class TopProducts:
    """Топ 8 товаров"""

    def get_top_8(self):
        """Получить топ-8 товаров"""
        pass

    def sort_by_sells_count(self):
        """Сортировка по количеству покупок товара"""
        pass


class HotOffers:
    """Горячие предложения. До 9 штук. С акциями."""

    def get_offers(self):
        pass


class LimitedEdition:
    """Товары, помеченные как Ограниченный тираж"""

    def get_limited_product(self):
        pass

    def check_if_in_limited_product(self):
        """Проверить является ли какой-либо из товаров товаром из блока Предложение дня и исключить его из выдачи"""
        pass


class ProductDiscount:
    """Скидки на продукт"""

    def apply(self):
        """Применить скидку"""
        pass


class SetDiscounts:
    """Скидки на наборы"""

    def apply(self):
        """Применить скидку"""
        pass


class CartDiscount:
    """Скидки на корзину"""

    def apply(self):
        """Применить скидку"""
        pass
