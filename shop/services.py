from shop.models import Shop, ShopImage
from product.models import Offer, Product
from config.settings.dev import COUNT_ELEMENTS_BEST_OFFER_SHOP



class ShopDetail:
    """Магазин"""

    count_top_products = 10

    def __init__(self, shop_id):
        self.shop_id = shop_id

    def get_shop_description(self):
        """Получить описание магазина"""
        description_shop = Shop.objects.get(id=self.shop_id)
        return description_shop

    def get_shop_photos(self):
        """Получить фотографии магазина"""
        pass

    def get_shop_address(self):
        """Получить адрес магазина для карт"""
        pass

    def get_top_products(self):
        """Получить топ товаров продавца"""
        top_products = Offer.objects.filter(shop=self.shop_id)[:COUNT_ELEMENTS_BEST_OFFER_SHOP]
        return top_products



class ShopList:
    """Магазины"""

    def get_list_shops(self):
        """Получить список всех магазинов"""
        pass