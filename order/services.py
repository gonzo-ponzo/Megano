from decimal import Decimal
from django.conf import settings
from order.models import Offer
from product.models import ProductImage, Product
from shop.models import Shop


class Cart(object):
    """
    Объект корзины
    """

    def __init__(self, request, user_cart={}):
        """
        Инициализация корзины
        """
        if request.user.is_authenticated:
            cart = user_cart
        else:
            self.session = request.session
            cart = self.session.get(settings.CART_SESSION_ID)
            if not cart:
                cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_idx = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_idx)
        for product in products:
            self.cart[str(product.id)]["product"] = product

        cart = self.cart
        for product in cart:
            cart[product]["current"] = {}
            for shop in cart[product]["offers"].keys():
                cart[product]["current"][shop] = {
                    "price": get_product_price_by_shop(int(shop), int(product)),
                    "quantity": cart[product]["offers"][shop],
                    "shop": get_shop_by_id(int(shop)),
                    "name": get_name_by_product(product_id=int(product)),
                    "image": get_main_pic_by_product(int(product)),
                    "product_id": int(product),
                    "shop_id": shop,
                }
                price = cart[product]["current"][shop]["price"]
                quantity = cart[product]["current"][shop]["quantity"]
                cart[product]["current"][shop]["total_price"] = price * quantity
                yield cart[product]["current"][shop]

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        total = 0
        for product in self.cart.keys():
            for quantity in self.cart[product]["offers"].values():
                total += quantity
        return total

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        total_price = 0
        for product in self.cart:
            for shop in self.cart[product]["offers"].keys():
                price = get_product_price_by_shop(int(shop), int(product))
                amount = self.cart[product]["offers"][shop]
                total_price += price * amount

        return Decimal(total_price)

    def add(self, request, product: Product, shop_id: int, quantity: int = 1, update_quantity: bool = False):
        """
        Добавление продукта в корзину
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"offers": {}}
        if update_quantity:
            self.cart[product_id]["offers"][str(shop_id)] = quantity
        else:
            if self.cart[product_id]["offers"].get(str(shop_id)):
                self.cart[product_id]["offers"][str(shop_id)] += quantity
                print(quantity)
            else:
                self.cart[product_id]["offers"][shop_id] = quantity
        self.save(request=request)

    def lower(self, request, product: Product, shop_id: int):
        """
        Уменьшение кол-ва товара в корзине
        """
        product_id = str(product.id)
        cart = self.cart
        if cart[product_id]["offers"][str(shop_id)] > 0:
            cart[product_id]["offers"][str(shop_id)] -= 1
        if cart[product_id]["offers"][str(shop_id)] == 0:
            del cart[product_id]["offers"][str(shop_id)]
        self.save(request)

    def save(self, request):
        if request.user.is_authenticated:
            request.user.save()
        else:
            self.session[settings.CART_SESSION_ID] = self.cart
            self.session.modified = True

    def remove(self, request, product: Product, shop_id: int):
        """
        Удаление продукта из корзины.
        """
        product_id = str(product.id)
        cart = self.cart

        if str(shop_id) in cart[product_id]["offers"]:
            del cart[product_id]["offers"][str(shop_id)]
            self.save(request)

    def clear(self):
        # Удаление корзины из сессии
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
