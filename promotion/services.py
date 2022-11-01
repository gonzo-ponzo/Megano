from django.core.cache import cache
from django.conf import settings
from constance import config
from .models import Banner, PromotionOffer


class BannerMain:
    """Баннеры на главной странице"""

    _count = 3

    @classmethod
    def get_active_banners(cls):
        """Получить нужное кол-во активных баннеров"""
        return (
            Banner.objects.filter(is_active=True)
            .only("pk", "name", "description", "product", "image", "product__id")
            .select_related("product").order_by("?")[:config.COUNT_BANNERS]
        )

    @classmethod
    def get_cache_banners(cls):
        """Получить кэш"""
        return cache.get_or_set(
            settings.CACHE_KEY_BANNER,
            cls.get_active_banners,
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


class DetailedPromotion:
    def __init__(self, promotion_offer: PromotionOffer):
        self.promotion = promotion_offer
