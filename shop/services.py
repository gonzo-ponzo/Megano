from shop.models import Shop, ShopImage



class ShopDetail:
    """Магазин"""

    def __init__(self, shop_id):
        self.shop_id = shop_id

    def get_shop_description(self):
        """Получить описание магазина"""
        description_shop = Shop.objects.get(id=0)   #Shop.objects.get(id=self.shop_id)
        print(3)
        print(description_shop.name)
        return description_shop

    def get_shop_photos(self):
        """Получить фотографии магазина"""
        pass

    def get_shop_address(self):
        """Получить адрес магазина для карт"""
        pass

    def get_top_10_products(self):
        """Получить топ 10 товаров продавца"""
        pass


class ShopList:
    """Магазины"""

    def get_list_shops(self):
        """Получить список всех магазинов"""
        pass