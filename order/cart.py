from decimal import Decimal
from django.conf import settings
from product.models import Product
from order.utils import get_product_price_by_shop, get_main_pic_by_product, \
    get_name_by_product, get_shop_by_id


class Cart(object):
    """
    Объект корзины
    """

    def __init__(self, request):
        """
        Инициализация корзины
        """
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
            self.cart[str(product.id)]['product'] = product

        cart = self.cart
        for product in cart:
            cart[product]['current'] = {}
            for shop in cart[product]['offers'].keys():
                cart[product]['current'][shop] = {
                    'price': get_product_price_by_shop(int(shop), int(product)),
                    'quantity': cart[product]['offers'][shop],
                    'shop': get_shop_by_id(int(shop)),
                    'name': get_name_by_product(product_id=int(product)),
                    'image': get_main_pic_by_product(int(product)),
                    'product_id': int(product),
                    'shop_id': shop
                }
                price = cart[product]['current'][shop]['price']
                quantity = cart[product]['current'][shop]['quantity']
                cart[product]['current'][shop]['total_price'] = price * quantity
                yield (
                    cart[product]['current'][shop]['price'],
                    str(cart[product]['current'][shop]['quantity']),
                    cart[product]['current'][shop]['shop'],
                    cart[product]['current'][shop]['name'],
                    cart[product]['current'][shop]['image'],
                    cart[product]['current'][shop]['product_id'],
                    cart[product]['current'][shop]['shop_id']
                )

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        total = 0
        for product in self.cart.keys():
            for quantity in self.cart[product]['offers'].values():
                total += quantity
        return total

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        total_price = 0
        cart = self.cart
        for product in cart:
            for shop in cart[product]['offers'].keys():
                total_price += get_product_price_by_shop(
                    int(shop), int(product)
                ) * cart[product]['offers'][shop]
        return Decimal(total_price)

    def add(self, product: Product, shop_id: int, quantity: int = 1,
            update_quantity: bool = False):
        """
        Добавление продукта в корзину
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'offers': {}
            }
        if update_quantity:
            self.cart[product_id]['offers'][str(shop_id)] = quantity
        else:
            if self.cart[product_id]['offers'].get(str(shop_id)):
                self.cart[product_id]['offers'][str(shop_id)] += quantity
            else:
                self.cart[product_id]['offers'][shop_id] = quantity
        self.save()

    def lower(self, product: Product, shop_id: int):

        product_id = str(product.id)
        cart = self.cart
        if cart[product_id]['offers'][str(shop_id)] > 0:
            cart[product_id]['offers'][str(shop_id)] -= 1
        if cart[product_id]['offers'][str(shop_id)] == 0:
            del cart[product_id]['offers'][str(shop_id)]
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product: Product, shop_id: int):
        """
        Удаление продукта из корзины.
        """
        product_id = str(product.id)
        cart = self.cart

        if str(shop_id) in cart[product_id]['offers']:
            del cart[product_id]['offers'][str(shop_id)]
            self.save()

    def clear(self):
        # Удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
