from order.models import Offer
from product.models import ProductImage, Product
from shop.models import Shop
from decimal import Decimal


def get_product_price_by_shop(shop_id: int, product_id: int):
    """
    Получение цены за ед. продукта
    """
    price = Decimal(Offer.objects.get(shop_id=shop_id, product_id=product_id).price)
    return price


def get_main_pic_by_product(product_id: int):
    """
    Получение главного изображения продукта
    """
    try:
        main_pic = ProductImage.objects.all().filter(product_id=product_id)[0].image
    except ProductImage.DoesNotExist:
        main_pic = None
    return main_pic


def get_name_by_product(product_id: int):
    """
    Получение наименования продукта
    """
    try:
        name = Product.objects.get(id=product_id).name
    except Product.DoesNotExist:
        name = None
    return name


def get_shop_by_id(shop_id: int):
    """
    Получение наименования магазина
    """
    try:
        shop = Shop.objects.get(id=shop_id).name
    except Shop.DoesNotExist:
        shop = None
    return shop
