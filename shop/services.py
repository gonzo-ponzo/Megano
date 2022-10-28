from django.db.models import Sum, Avg, Q, Max, DecimalField
from django.db.models.functions import Cast

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
        )
        top_products = top_products.annotate(
            sorted_amount_offers_buy=Sum('orderoffer__amount')
        )
        top_products = top_products.order_by(
            '-sorted_amount_offers_buy'
        )[:COUNT_ELEMENTS_BEST_OFFER_SHOP]
        top_products = top_products.annotate(
            rating=Avg('product__review__rating', default=0)
        )
        top_products = top_products.annotate(
            discount_decimals=Max('promotionoffer__discount_decimals', filter=Q(
                promotionoffer__discount_type_id=1,
                promotionoffer__is_active=True
            )),
            discount_decimals_price=Max('price') - Max('promotionoffer__discount_decimals', filter=Q(
                promotionoffer__discount_type_id=1,
                promotionoffer__is_active=True
            )),
            discount_percentage=Max('promotionoffer__discount_percentage', filter=Q(
                promotionoffer__discount_type_id=1,
                promotionoffer__is_active=True
            )),
            discount_percentage_price=Cast(Max('price') -
                                           Cast(
                                               Max(
                                                   'promotionoffer__discount_percentage',
                                                   filter=Q(
                                                       promotionoffer__discount_type_id=1,
                                                       promotionoffer__is_active=True
                                                   )
                                               ),
                                               DecimalField(
                                                   max_digits=6,
                                                   decimal_places=2
                                               )
                                           ) /
                                           Cast(
                                               100,
                                               DecimalField(
                                                   max_digits=6,
                                                   decimal_places=2
                                               )
                                           ) *
                                           Max(
                                               'price'
                                           ),
                                           DecimalField(
                                               max_digits=6,
                                               decimal_places=2
                                           )
                                           )
        )
        return top_products


class ShopList:
    """Магазины"""

    def get_list_shops(self):
        """Получить список всех магазинов"""
        list_shops = Shop.objects.filter(
            offer__amount__gt=0,
            offer__deleted_at=None,
            product__deleted_at=None
        ).distinct()
        return list_shops
