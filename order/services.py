from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db import transaction, DatabaseError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Prefetch
from django.http import Http404
from order.models import Offer, Delivery, Order, OrderOffer
from product.models import ProductImage, Product
from shop.models import Shop
from promotion.models import PromotionOffer
from .queries import USER_ORDERS_SQL, USER_LAST_ORDER_SQL, ORDER_SQL
from decimal import Decimal
from typing import Dict, Tuple
import json


class Cart(object):
    """
    Объект корзины
    """

    def __getitem__(self, item):
        """
        Получение атрибутов корзины
        """
        return self.cart[item]

    def __init__(self, request):
        """
        Инициализация корзины
        """
        self.request = request

        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        if request.user.is_authenticated:
            self.cart = request.user.cart
            if not cart == {}:
                for shop in cart.keys():
                    for product in cart[shop]:
                        quantity = cart[shop][product]["quantity"]
                        if self.cart.get(shop):
                            if self.cart[shop].get(product):
                                if self.cart[shop][product]["quantity"] < quantity:
                                    self.cart[shop][product] = cart[shop][product]
                            else:
                                self.cart[shop][product] = cart[shop][product]
                        else:
                            self.cart[shop] = cart[shop]
                self.save()
                self.session[settings.CART_SESSION_ID] = {}
        else:
            self.cart = cart

    def __iter__(self):
        """
        Перебор элементов в корзине и получение данных из базы данных.
        """
        for shop in self.cart:
            for product in self.cart[shop].keys():
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
        promotion_offers = PromotionOffer.objects.prefetch_related().filter(offer=offer, is_active=True).all()

        for promotion in promotion_offers:
            # Временная акция на товар
            if promotion.discount_type_id.id == 1:
                self.get_discount_one(shop_id, product_id, promotion)

            # Скидка на N-ый товар бесплатно
            elif promotion.discount_type_id.id == 2:
                self.get_discount_two(shop_id, product_id, promotion)

            # Скидка на сумму корзины
            elif promotion.discount_type_id.id == 3:
                self.get_discount_three(shop_id, promotion)

            # Скидка при покупке более N товаров в корзине
            elif promotion.discount_type_id.id == 4:
                self.get_discount_four(shop_id, promotion)

            # Скидка при покупке с товаром из N категории
            elif promotion.discount_type_id.id == 5:
                self.get_discount_five(shop_id, product_id, promotion)

    def get_discount_one(self, shop_id: str, product_id: str, promotion: PromotionOffer):
        self.cart[shop_id][product_id].setdefault("discount", {promotion.id: 0})

        if promotion.discount_decimals != 0:
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = round(
                float(promotion.discount_decimals), 2
            )

        else:
            price = self.cart[shop_id][product_id]["price"]
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = round(
                float(price * (100 - promotion.discount_percentage) / 100), 2
            )

    def get_discount_two(self, shop_id: str, product_id: str, promotion: PromotionOffer):
        self.cart[shop_id][product_id].setdefault("discount", {promotion.id: 0})
        price = self.cart[shop_id][product_id]["offer_price"]
        quantity = self.cart[shop_id][product_id]["quantity"]
        discount_value = promotion.discount_type_value

        if quantity == 0:
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = 0
        else:
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = round(
                float(quantity // discount_value * price / quantity), 2
            )

    def get_discount_three(self, shop_id: str, promotion: PromotionOffer):
        shop_cart_price = 0
        shop_cart_amount = 0
        products = [offer.product_id for offer in promotion.offer.prefetch_related().all()]

        for product in self.cart[shop_id].keys():
            if int(product) in products:
                quantity = self.cart[shop_id][product]["quantity"]
                price = self.cart[shop_id][product]["offer_price"]
                shop_cart_price += quantity * price
                shop_cart_amount += quantity

        if shop_cart_price >= promotion.discount_type_value:
            for product in self.cart[shop_id].keys():
                if int(product) in products:
                    self.cart[shop_id][product].setdefault("discount", {promotion.id: 0})

                    if promotion.discount_decimals != 0:
                        self.cart[shop_id][product]["discount"][str(promotion.id)] = round(
                            float(promotion.discount_decimals / shop_cart_amount), 2
                        )

                    else:
                        self.cart[shop_id][product]["discount"][str(promotion.id)] = int(
                            round(float(shop_cart_price * promotion.discount_percentage / 100 / shop_cart_amount), 2)
                        )

        else:
            for product in self.cart[shop_id]:
                if int(product) in products:
                    self.cart[shop_id][product]["discount"][str(promotion.id)] = 0

    def get_discount_four(self, shop_id: str, promotion: PromotionOffer):
        shop_cart_amount = 0
        products = [offer.product_id for offer in promotion.offer.prefetch_related().all()]

        for product in self.cart[shop_id].keys():
            if int(product) in products:
                self.cart[shop_id][product].setdefault("discount", {promotion.id: 0})
                quantity = self.cart[shop_id][product]["quantity"]
                shop_cart_amount += quantity

        if shop_cart_amount >= promotion.discount_type_value:
            for product in self.cart[shop_id]:
                if int(product) in products:

                    if promotion.discount_decimals != 0:
                        self.cart[shop_id][product]["discount"][str(promotion.id)] = round(
                            float(promotion.discount_decimals / shop_cart_amount), 2
                        )

                    else:
                        price = self.cart[shop_id][product]["offer_price"]
                        self.cart[shop_id][product]["discount"][str(promotion.id)] = round(
                            float(price * promotion.discount_percentage / 100), 2
                        )

        else:
            for product in self.cart[shop_id]:
                self.cart[shop_id][product]["discount"][str(promotion.id)] = 0

    def get_discount_five(self, shop_id: str, product_id: str, promotion):
        flag = True
        quantity = self.cart[shop_id][product_id]["quantity"]
        for product in self.cart[shop_id]:
            if get_product_category_id(product) == promotion.discount_type_value:
                flag = False

                if promotion.discount_decimals != 0:
                    self.cart[shop_id][product_id]["discount"][str(promotion.id)] = round(
                        float(promotion.discount_decimals / quantity), 2
                    )
                    break

                else:
                    price = self.cart[shop_id][product_id]["offer_price"]
                    self.cart[shop_id][product_id]["discount"][str(promotion.id)] = round(
                        float(price * promotion.discount_percentage / 100 / quantity), 2
                    )
                    break

        if flag:
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = 0

        self.save()

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        total_price = 0
        for shop in self.cart.keys():
            for product in self.cart[shop].keys():
                price = self.cart[shop][product]["final_price"]
                amount = self.cart[shop][product]["quantity"]
                total_price += price * amount

        return round(total_price, 2)

    def check_limits(self, product_id: str, shop_id: str):
        """
        Проверка остатков продукта на складе
        """
        limits = get_object_or_404(Offer, product_id=product_id, shop_id=shop_id).amount
        try:
            cart_amount = self.cart[shop_id][product_id]["quantity"]
        except KeyError:
            cart_amount = 1
        return cart_amount < limits

    def get_total_discount(self, product: str, shop: str):
        """
        Подсчет итоговой скидки продукта в корзине
        """
        if self.cart[shop][product].get("offer_price"):
            self.cart[shop][product]["final_price"] = round(float(self.cart[shop][product]["offer_price"]), 2)
        else:
            self.cart[shop][product]["final_price"] = round(
                float(get_object_or_404(Offer, product=product, shop=shop).price), 2
            )

        self.cart[shop][product].setdefault("discount", {"0": 0})
        for discount in self.cart[shop][product]["discount"].values():
            self.cart[shop][product]["final_price"] -= round(float(discount), 2)
        if self.cart[shop][product]["final_price"] < 0:
            self.cart[shop][product]["final_price"] = 0
        self.save()

    def update(self, product_id: int, shop_id: int):
        """
        Обновление данных в корзине
        """
        self.cart[shop_id].setdefault(product_id, {"quantity": 1})
        self.cart[shop_id][product_id].setdefault("discount", {0: 0})
        item = self.cart[shop_id][product_id]
        item["offer_id"] = get_offer_id(shop_id, product_id)
        item["shop_id"] = shop_id
        item["shop_name"] = get_shop_by_id(shop_id)
        item["product_id"] = product_id
        item["product_name"] = get_name_by_product(product_id)
        item["product_image"] = get_main_pic_by_product(product_id)
        item["offer_price"] = get_product_price_by_shop(shop_id, product_id)
        item["limits"] = get_shop_limit(shop_id, product_id)
        for discount in item["discount"]:
            if not PromotionOffer.objects.filter(is_active=True, id=int(discount)):
                item["discount"][discount] = 0
        for shop in self.cart:
            for product in self.cart[shop]:
                self.get_discount_price(product, shop)
                self.get_total_discount(product, shop)
        self.save()

    def refresh(self):
        for shop in self.cart.keys():
            for product in self.cart[shop].keys():
                self.update(product, shop)
        self.save()

    def add(self, product_id: int, shop_id: int, quantity: int = 1, update_quantity: bool = False):
        """
        Добавление продукта в корзину
        """
        if not self.cart.get(shop_id):
            self.cart[shop_id] = {}
        if update_quantity:
            self.cart[shop_id][product_id] = {"quantity": quantity}

        if product_id not in self.cart[shop_id]:
            self.update(product_id, shop_id)
        else:
            self.cart[shop_id][product_id]["quantity"] += 1
            self.update(product_id, shop_id)

        self.save()

    def lower(self, product_id: str, shop_id: str):
        """
        Уменьшение кол-ва товара в корзине
        """
        if self.cart[shop_id][product_id]["quantity"] > 0:
            self.cart[shop_id][product_id]["quantity"] -= 1

        if self.cart[shop_id][product_id]["quantity"] == 0:
            del self.cart[shop_id][product_id]
            if self.cart[shop_id] == {}:
                del self.cart[shop_id]

        for shop in self.cart:
            for product in self.cart[shop]:
                self.get_discount_price(product, shop)
                self.get_total_discount(product, shop)
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

        for shop in self.cart.keys():
            for product in self.cart[shop].keys():
                self.get_discount_price(product, shop)
                self.get_total_discount(product, shop)
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


class Checkout:
    """Оформление заказа"""

    delivery_key = ("normal", "express")

    @classmethod
    def get_data_from_cart(cls, shops: Dict, user_id: int) -> Dict:
        """Формирование данных из корзины"""
        data_products = []
        full_total_price = 0
        total_price = 0

        for products in shops.values():
            for product in products.values():
                product["discount"] = Decimal(str(sum(product.pop("discount").values())))
                full_total_price += product.get("quantity", 1) * Decimal(str(product.get("offer_price")))
                total_price += product.get("quantity", 1) * Decimal(str(product.get("final_price")))
                data_products.append(product)

        delivery_id, total = cls._get_data_delivery(
            shop_cnt=len(shops), full_total_price=full_total_price, total_price=total_price
        )

        order = {"products": data_products, "delivery_id": delivery_id, "total": total}
        SerializersCache.set_data_in_cache(
            f"{settings.CACHE_KEY_CHECKOUT}{user_id}", order, settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_CHECKOUT)
        )
        return order

    @classmethod
    def _get_data_delivery(cls, shop_cnt: int, full_total_price: Decimal, total_price: Decimal) -> Tuple[int, Dict]:
        """Формирования итоговых цен с учетом доставки"""
        delivery = Delivery.objects.order_by("-created_at").first()
        total = {}

        for key in cls.delivery_key:
            if key == cls.delivery_key[0]:
                if shop_cnt == 1 and total_price > delivery.sum_order:
                    delivery_price = 0
                else:
                    delivery_price = delivery.price
            else:
                delivery_price = delivery.price + delivery.express_price

            total[key] = {
                "delivery_price": delivery_price,
                "full_total_price": full_total_price + delivery_price,
                "total_price": total_price + delivery_price,
            }

        return delivery.pk, total


class OrderPaymentCache:
    """Добавление заказа для оплаты"""

    __key_cache = settings.CACHE_KEY_PAYMENT_ORDER
    __timeout_cache = settings.CACHE_TIMEOUT.get(__key_cache)

    @classmethod
    def get_cache_order_for_payment(cls, order_id: int, user_id: int) -> Dict | None:
        """Получить данные по заказу"""
        order_cache = cache.get(cls.__key_cache.format(user_id=user_id, order_id=order_id))
        if order_cache:
            return order_cache
        return cls._get_data_with_order_detail(order_id, user_id)

    @classmethod
    def _get_data_with_order_detail(cls, order_id: int, user_id: int) -> Dict | None:
        """Добавление в кэш и получение данных, если статус соответствующий"""
        order = OrderHistory.get_history_order_detail(order_id, user_id)
        order_status = [
            status[0]
            for status in Order.STATUS_CHOICES
            if status[1] in ("Новый заказ", "Ожидается оплата", "Не оплачен")
        ]
        if order.status_type in order_status:
            return cls.set_data_with_order(order)

    @classmethod
    def set_data_with_order(cls, order: Order, price: Decimal = None) -> Dict:
        """Добавляется заказ в кэш"""
        total_price = price if price else order.total_full_price
        data = {"order": order, "total_price": total_price}
        cache.set(cls.__key_cache.format(user_id=order.user_id, order_id=order.id), data, cls.__timeout_cache)
        return data


class SerializersCache:
    """Класс для работы с данными из кэша"""

    @staticmethod
    def set_data_in_cache(cache_key: str, data: Dict, cache_ttl: int) -> None:
        cache.set(cache_key, json.dumps(data, cls=DjangoJSONEncoder), cache_ttl)

    @staticmethod
    def get_data_from_cache(cache_key: str) -> Dict | None:
        data = cache.get(cache_key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    def clean_data_from_cache(cache_key: str) -> None:
        cache.delete(cache_key)


class CheckoutDB:
    """Сохранение заказа в БД"""

    def __init__(self, user_id: int, order_info: Dict, order_data: Dict, cart: Cart):
        self.__user_id = user_id
        self.__order_info = order_info
        self.__order_data = order_data
        self.__cart = cart

    def _add_data_order(self) -> Order:
        order = Order.objects.create(
            user_id=self.__user_id, delivery_id=self.__order_data.get("delivery_id"), **self.__order_info
        )
        return order

    def _add_data_order_offer(self, order: Order) -> None:
        order_offer = []
        for product in self.__order_data.get("products"):
            order_offer.append(
                OrderOffer(
                    order=order,
                    offer_id=product.get("offer_id"),
                    price=product.get("offer_price"),
                    discount=product.get("discount"),
                    amount=product.get("quantity"),
                )
            )
        OrderOffer.objects.bulk_create(order_offer)

    def save_order(self) -> Tuple[bool, str, int | None]:
        try:
            with transaction.atomic():
                order = self._add_data_order()
                self._add_data_order_offer(order)
        except DatabaseError:
            return False, "Ошибка сервера", None

        type_delivery = Checkout.delivery_key[0] if order.delivery_type == 1 else Checkout.delivery_key[1]
        price = self.__order_data.get("total").get(type_delivery).get("total_price")
        OrderPaymentCache.set_data_with_order(order, price)
        self._clean_cache()

        return True, "Заказ сформирован", order.id

    def _clean_cache(self) -> None:
        SerializersCache.clean_data_from_cache(f"{settings.CACHE_KEY_CHECKOUT}{self.__user_id}")
        self.__cart.clear()

    @staticmethod
    def set_order_payment_type(order: Order, payment_type: int) -> Order:
        order_p = order.payment_type
        if order.payment_type != payment_type:
            order.payment_type = payment_type
            order.save()
            order.refresh_from_db()
        return order

    def set_order_status(self):
        """Изменить статус заказа"""
        pass

    def set_order_error(self):
        """Добавить ошибку"""
        pass


class OrderHistory:
    """История заказов"""

    @staticmethod
    def get_history_orders(user_id: int) -> Order | None:
        """Получить список заказов"""
        return Order.objects.raw(USER_ORDERS_SQL, [user_id])

    @staticmethod
    def get_history_last_order(user_id: int) -> Order | None:
        """Получить последний заказ"""
        try:
            order = Order.objects.raw(USER_LAST_ORDER_SQL, [user_id])[0]
        except IndexError:
            return None
        return order

    @staticmethod
    def get_history_order_detail(order_id: int, user_id: int) -> Order | None:
        """Получить детальную информацию о заказе"""
        try:
            order = Order.objects.raw(ORDER_SQL, [order_id, user_id])[0]
        except IndexError:
            raise Http404
        return order

    @staticmethod
    def get_products_order(order_id: int) -> OrderOffer:
        product_image = ProductImage.objects.only("image", "product_id")
        queryset = OrderOffer.objects.select_related("offer", "offer__product", "offer__shop")
        queryset = queryset.prefetch_related(Prefetch("offer__product__productimage_set", queryset=product_image))
        queryset = queryset.annotate(total_price=F("price") - F("discount"))
        queryset = queryset.filter(order_id=order_id)
        queryset = queryset.only(
            "id", "price", "discount", "amount", "offer_id", "offer__product__name", "offer__shop__name"
        )
        return queryset


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
    return get_object_or_404(Offer, shop_id=shop_id, product_id=product_id).amount


def get_offer_id(shop: int, product: int):
    return get_object_or_404(Offer, product=product, shop=shop).id


def get_product_category(product_id: str):
    return get_object_or_404(Product, id=product_id).category


def get_product_category_id(product_id: str):
    return get_object_or_404(Product, id=product_id).category.id
