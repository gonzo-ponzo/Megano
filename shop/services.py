from django.db.models import Sum

from shop.models import Shop, ShopImage
from product.models import Offer
from config.settings.base import COUNT_ELEMENTS_BEST_OFFER_SHOP


class ShopDetail:
    """Магазин"""

    def __init__(self, shop):
        self.shop = shop

    def get_shop_status(self):
        check = Shop.objects.filter(id=self.shop).first()
        if check:
            return True
        return False

    def get_shop_description(self):
        """Получить описание магазина"""
        description_shop = Shop.objects.get(id=self.shop)
        return description_shop

    def get_shop_photos(self):
        """Получить фотографии магазина"""
        shop_photos = list(ShopImage.objects.filter(shop=self.shop))
        return shop_photos

    def get_top_products(self):
        """Получить топ товаров продавца"""
        top_products = Offer.objects.filter(
            shop=self.shop,
            amount__gt=0,
            deleted_at=None,
            orderoffer__amount__gt=0
        ).annotate(
            sorted_amount_offers_buy=Sum('orderoffer__amount')
        ).order_by(
            '-sorted_amount_offers_buy'
        )[:COUNT_ELEMENTS_BEST_OFFER_SHOP]
        return top_products


class ShopList:
    """Магазины"""

    def get_list_shops(self):   #нужно сделать перепроверку разных комбинаций удаления и с 0 к продукту и офферам.
        """Получить список всех магазинов"""
        list_shops = Shop.objects.filter(
            offer__amount__gt=0,
            offer__deleted_at=None,
            product__deleted_at=None
        ).distinct()
        return list_shops
