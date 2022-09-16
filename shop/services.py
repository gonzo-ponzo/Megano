from shop.models import Shop, ShopImage
from product.models import Offer
from config.settings.base import COUNT_ELEMENTS_BEST_OFFER_SHOP


class ShopDetail:
    """Магазин"""

    count_top_products = 10

    def __init__(self, shop):
        self.shop = shop

    def get_shop_description(self):
        """Получить описание магазина"""
        description_shop = Shop.objects.values().get(id=self.shop)
        return description_shop

    def get_shop_photos(self):
        """Получить фотографии магазина"""
        shop_photos = list(ShopImage.objects.filter(shop=self.shop).values_list('image'))
        return shop_photos

    def get_shop_address(self):
        """Получить адрес магазина для карт"""
        pass

    def get_top_products(self):
        """Получить топ товаров продавца"""
        top_products = Offer.objects.filter(
            shop=self.shop
        )[:COUNT_ELEMENTS_BEST_OFFER_SHOP].select_related('product')
        return top_products


class ShopList:
    """Магазины"""

    def get_list_shops(self):
        """Получить список всех магазинов"""
        pass
