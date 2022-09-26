from decimal import Decimal
from django.conf import settings
from order.models import Offer
from product.models import ProductImage, Product
from shop.models import Shop
from django.shortcuts import get_object_or_404


class Cart(object):
    """
    Объект корзины
    """

    def __getitem__(self, item):
        return self.cart[item]

    def __init__(self, request):
        """
        Инициализация корзины
        """
        if request.user.is_authenticated:
            cart = request.user.cart
        else:
            self.session = request.session
            cart = self.session.get(settings.CART_SESSION_ID)
            if not cart:
                cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def __iter__(self):
        """
        Перебор элементов в корзине и получение данных из базы данных.
        """
        for shop in self.cart:
            for product in self.cart[shop].keys():
                item = self.cart[shop][product]
                item["shop_id"] = shop
                item["shop_name"] = get_shop_by_id(shop)
                item["product_id"] = product
                item["product_name"] = get_name_by_product(product)
                item["product_image"] = get_main_pic_by_product(product)
                item["offer_price"] = get_product_price_by_shop(shop, product)
                item["limits"] = get_shop_limit(shop, product)
                yield self.cart[shop][product]

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        total = 0
        for shop in self.cart:
            for product in self.cart[shop]:
                total += self.cart[shop][product]["quantity"]
        return total

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        total_price = 0
        for shop in self.cart:
            for product in self.cart[shop]:
                price = get_product_price_by_shop(shop, product)
                amount = self.cart[shop][product]["quantity"]
                total_price += price * amount

        return Decimal(total_price)

    def check_limits(self, product_id: str, shop_id: str):
        limits = get_object_or_404(Offer, product_id=product_id, shop_id=shop_id).amount
        try:
            cart_amount = self.cart[shop_id][product_id]["quantity"]
        except Exception:
            cart_amount = 1
        return cart_amount < limits

    def add(self, request, product_id: str, shop_id: str, quantity: int = 1, update_quantity: bool = False):
        """
        Добавление продукта в корзину
        """
        if not self.cart.get(shop_id):
            self.cart[shop_id] = {}
        if update_quantity:
            self.cart[shop_id][product_id] = {"quantity": quantity}
        if product_id not in self.cart[shop_id]:
            self.cart[shop_id] = {product_id: {"quantity": 1}}
        else:
            self.cart[shop_id][product_id]["quantity"] += 1
        self.save(request)

    def lower(self, request, product_id: str, shop_id: str):
        """
        Уменьшение кол-ва товара в корзине
        """
        if self.cart[shop_id][product_id]["quantity"] > 0:
            self.cart[shop_id][product_id]["quantity"] -= 1
        if self.cart[shop_id][product_id]["quantity"] == 0:
            del self.cart[shop_id][product_id]
            if self.cart[shop_id] == {}:
                del self.cart[shop_id]
        self.save(request)

    def save(self, request):
        """
        Сохранение корзины
        """
        if request.user.is_authenticated:
            request.user.save()
        else:
            self.session[settings.CART_SESSION_ID] = self.cart
            self.session.modified = True

    def remove(self, request, product_id: str, shop_id: int):
        """
        Удаление продукта из корзины.
        """
        if product_id in self.cart[shop_id]:
            del self.cart[shop_id][product_id]
            if self.cart[shop_id] == {}:
                del self.cart[shop_id]
            self.save(request)

    def clear(self, request):
        """
        # Удаление корзины из сессии
        """
        if request.user.is_authenticated:
            request.user.cart = {}
            request.user.save()
        else:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True


class Order:
    """
    Составление заказа
    """

    def set_user_param(self):
        """Уточнить параметры пользователя"""
        pass

    def set_shipping_param(self):
        """Установить параметры доставки"""
        pass

    def set_pay_param(self):
        """Установить параметры доставки"""
        pass

    def get_order_status(self):
        """Получить статус заказа"""
        pass

    def set_order_status(self):
        """Изменить статус заказа"""
        pass


class OrderHistory:
    """История покупок"""

    def add_product_in_history(self):
        """Добавить продукт в историю покупок"""
        pass

    def get_history(self):
        """Получить историю покупок"""
        pass


def get_product_price_by_shop(shop_id: int, product_id: int):
    """
    Получение цены за ед. продукта
    """
    return Decimal(Offer.objects.get(shop_id=shop_id, product_id=product_id).price)


def get_main_pic_by_product(product_id: int):
    """
    Получение главного изображения продукта
    """
    return ProductImage.objects.all().filter(product_id=product_id)[0].image


def get_name_by_product(product_id: int):
    """
    Получение наименования продукта
    """
    return get_object_or_404(Product, id=product_id).name


def get_shop_by_id(shop_id: int):
    """
    Получение наименования магазина
    """
    return get_object_or_404(Shop, id=shop_id).name


def get_shop_limit(shop_id: int, product_id: int):
    """
    Получение остатка по предложению магазина
    """
    return get_object_or_404(Offer, shop_id=shop_id, product_id=product_id).amount
