from django.core.cache import cache
from django.conf import settings
from constance import config
from .models import Banner, PromotionOffer


class BannerMain:
    """Баннеры на главной странице"""

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
        """Получить/добавить кэш"""
        return cache.get_or_set(
            settings.CACHE_KEY_BANNER,
            cls.get_active_banners,
            settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_BANNER),
        )


class DetailedPromotion:
    def __init__(self, promotion_offer: PromotionOffer):
        self.promotion = promotion_offer
