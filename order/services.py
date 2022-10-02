from decimal import Decimal
from django.conf import settings
from order.models import Offer
from product.models import ProductImage, Product
from shop.models import Shop
from django.shortcuts import get_object_or_404
from promotion.models import PromotionOffer, DiscountType


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

        self.request = request
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
        for shop in self.cart:
            for product in self.cart[shop]:
                # self.get_discount_price(product, shop)
                # self.get_total_discount(product, shop)
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

    def get_discount_price(self, product_id: str, shop_id: str):
        """
        Получение величины скидки на основе корзины
        """
        offer = get_object_or_404(Offer, product_id=product_id, shop_id=shop_id)
        promotion_offers = PromotionOffer.objects.filter(offer=offer,
                                                         is_active=True).all()

        for promotion in promotion_offers:

            # Временная акция на товар
            if promotion.discount_type_id.id == 1:
                self.cart[shop_id][product_id].setdefault("discount", {promotion.id: 0})

                if promotion.discount_decimals != 0:
                    self.cart[shop_id][product_id]["discount"][str(promotion.id)] = promotion.discount_decimals

                else:
                    price = self.cart[shop_id][product_id]["price"]
                    self.cart[shop_id][product_id]["discount"][str(promotion.id)] = price * (100 - promotion.discount_percentage) / 100

            # Скидка на N-ый товар бесплатно
            elif promotion.discount_type_id.id == 2:
                self.cart[shop_id][product_id].setdefault("discount", {promotion.id: 0})
                if self.cart[shop_id][product_id].get("offer_price"):
                    price = self.cart[shop_id][product_id]["offer_price"]
                else:
                    price = int(get_object_or_404(Offer, product_id=product,
                                              shop_id=shop_id).price)
                quantity = self.cart[shop_id][product_id]["quantity"]
                discount_value = promotion.discount_type_value

                if quantity == 0:
                    self.cart[shop_id][product_id]["discount"][str(promotion.id)] = 0
                else:
                    self.cart[shop_id][product_id]["discount"][str(promotion.id)] = (quantity // discount_value) * price / quantity

            # Скидка на сумму корзины
            elif promotion.discount_type_id.id == 3:
                shop_cart_price = 0
                shop_cart_amount = 0

                for product in self.cart[shop_id]:
                    quantity = self.cart[shop_id][product]["quantity"]
                    if self.cart[shop_id][product].get("offer_price"):
                        price = self.cart[shop_id][product]["offer_price"]
                    else:
                        price = int(get_object_or_404(Offer, product_id=product, shop_id=shop_id).price)
                    shop_cart_price += quantity * price
                    shop_cart_amount += quantity

                if shop_cart_price >= promotion.discount_type_value:
                    for product in self.cart[shop_id]:
                        self.cart[shop_id][product].setdefault("discount", {
                            promotion.id: 0})

                        if promotion.discount_decimals != 0:
                            self.cart[shop_id][product]["discount"][str(promotion.id)] = promotion.discount_decimals // shop_cart_amount

                        else:
                            if self.cart[shop_id][product].get("offer_price"):
                                price = self.cart[shop_id][product]["offer_price"]
                            else:
                                price = int(get_object_or_404(Offer, product=product, shop_id=shop_id).price)
                            self.cart[shop_id][product]["discount"][str(promotion.id)] = int(price * promotion.discount_percentage / 100)

                else:
                    for product in self.cart[shop_id]:
                        self.cart[shop_id][product]["discount"][
                            str(promotion.id)] = 0

            # Скидка при покупке более N товаров в корзине
            elif promotion.discount_type_id.id == 4:
                shop_cart_amount = 0

                for product in self.cart[shop_id]:
                    self.cart[shop_id][product].setdefault("discount", {
                        promotion.id: 0})
                    quantity = self.cart[shop_id][product]["quantity"]
                    shop_cart_amount += quantity

                if shop_cart_amount >= promotion.discount_type_value:
                    for product in self.cart[shop_id]:

                        if promotion.discount_decimals != 0:
                            self.cart[shop_id][product]["discount"][str(promotion.id)] = promotion.discount_decimals / shop_cart_amount

                        else:
                            price = self.cart[shop_id][product]["offer_price"]
                            self.cart[shop_id][product]["discount"][str(promotion.id)] = price * (
                                        100 - promotion.discount_percentage) / 100

                else:
                    for product in self.cart[shop_id]:
                        self.cart[shop_id][product]["discount"][
                            str(promotion.id)] = 0

            # Скидка при покупке с товаром из N категории
            elif promotion.discount_type_id.id == 5:
                flag = True

                for product in self.cart[shop_id]:
                    if get_product_category_id(product) == promotion.discount_type_value:
                        flag = False

                        if promotion.discount_decimals != 0:
                            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = promotion.discount_decimals
                            break

                        else:
                            price = self.cart[shop_id][product_id]["price"]
                            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = price * (
                                        100 - promotion.discount_percentage) / 100
                            break

                if flag:
                    self.cart[shop_id][product_id]["discount"][str(promotion.id)] = 0

        self.save()
                    
    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        total_price = 0
        for shop in self.cart:
            for product in self.cart[shop]:

                if self.cart[shop][product].get("final_price") and self.cart[shop][product].get("final_price") > 0:
                    price = self.cart[shop][product]["final_price"]
                    amount = self.cart[shop][product]["quantity"]

                else:
                    price = get_product_price_by_shop(shop, product)
                    amount = self.cart[shop][product]["quantity"]

                total_price += price * amount

        return Decimal(total_price)

    def check_limits(self, product_id: str, shop_id: str):
        """
        Проверка остатков продукта на складе
        """
        limits = get_object_or_404(Offer, product_id=product_id,
                                   shop_id=shop_id).amount
        try:
            cart_amount = self.cart[shop_id][product_id]["quantity"]
        except Exception:
            cart_amount = 1
        return cart_amount < limits

    def get_total_discount(self, product: str, shop: str):
        """
        Подсчет итоговой скидки продукта в корзине
        """
        if self.cart[shop][product].get("offer_price"):
            self.cart[shop][product]["final_price"] = int(self.cart[shop][product]["offer_price"])
        else:
            self.cart[shop][product]["final_price"] = int(get_object_or_404(Offer, product=product,
                                      shop=shop).price)

        self.cart[shop][product].setdefault("discount", {
            "0": 0})
        for discount in self.cart[shop][product]["discount"].values():
            self.cart[shop][product]["final_price"] -= int(discount)
        self.save()

    def add(self, product_id: str, shop_id: str, quantity: int = 1,
            update_quantity: bool = False):
        """
        Добавление продукта в корзину
        """
        if not self.cart.get(shop_id):
            self.cart[shop_id] = {}
        if update_quantity:
            self.cart[shop_id][product_id] = {"quantity": quantity}

        if product_id not in self.cart[shop_id]:
            self.cart[shop_id].setdefault(product_id, {"quantity": 1})
        else:
            self.cart[shop_id][product_id]["quantity"] += 1

        self.get_discount_price(product_id, shop_id)
        self.get_total_discount(product_id, shop_id)
        self.save()

    def lower(self, product_id: str, shop_id: str):
        """
        Уменьшение кол-ва товара в корзине
        """
        if self.cart[shop_id][product_id]["quantity"] > 0:
            self.cart[shop_id][product_id]["quantity"] -= 1
            self.get_discount_price(product_id, shop_id)
            self.get_total_discount(product_id, shop_id)

        if self.cart[shop_id][product_id]["quantity"] == 0:
            del self.cart[shop_id][product_id]
            if self.cart[shop_id] == {}:
                del self.cart[shop_id]

        self.save()

    def save(self):
        """
        Сохранение корзины
        """
        if self.request.user.is_authenticated:
            self.request.user.save()
        else:
            self.session[settings.CART_SESSION_ID] = self.cart
            self.session.modified = True

    def remove(self, product_id: str, shop_id: int):
        """
        Удаление продукта из корзины.
        """
        if product_id in self.cart[shop_id]:
            del self.cart[shop_id][product_id]
            if self.cart[shop_id] == {}:
                del self.cart[shop_id]

        self.save()

    def clear(self):
        """
        # Удаление корзины из сессии
        """
        if self.request.user.is_authenticated:
            self.request.user.cart = {}
            self.request.user.save()
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
    return float(get_object_or_404(Offer, product_id=product_id, shop_id=shop_id).price)


def get_main_pic_by_product(product_id: int):
    """
    Получение главного изображения продукта
    """
    try:
        return str(ProductImage.objects.all().filter(product_id=product_id)[0].image)
    except IndexError:
        return None


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
    return get_object_or_404(Offer, shop_id=shop_id,
                             product_id=product_id).amount


def get_product_category(product_id: str):
    return get_object_or_404(Product, id=product_id).category


def get_product_category_id(product_id: str):
    return get_object_or_404(Product, id=product_id).category.id
