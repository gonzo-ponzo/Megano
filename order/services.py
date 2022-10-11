from decimal import Decimal
from django.conf import settings
from order.models import Offer, Delivery
from product.models import ProductImage, Product
from shop.models import Shop
from django.shortcuts import get_object_or_404
from promotion.models import PromotionOffer
from typing import Dict, Tuple


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
            self.cart[shop_id][product_id]["discount"][
                str(promotion.id)] = round(float(promotion.discount_decimals), 2)

        else:
            price = self.cart[shop_id][product_id]["price"]
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = (
                round(float(price * (100 - promotion.discount_percentage) / 100, 2))
            )

    def get_discount_two(self, shop_id: str, product_id: str, promotion: PromotionOffer):
        self.cart[shop_id][product_id].setdefault("discount", {promotion.id: 0})
        if self.cart[shop_id][product_id].get("offer_price"):
            price = self.cart[shop_id][product_id]["offer_price"]
        else:
            price = int(get_object_or_404(Offer, product_id=product_id,
                                          shop_id=shop_id).price)
        quantity = self.cart[shop_id][product_id]["quantity"]
        discount_value = promotion.discount_type_value

        if quantity == 0:
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = 0
        else:
            self.cart[shop_id][product_id]["discount"][str(promotion.id)] = (
                round(float((quantity // discount_value) * price / quantity, 2))
            )

    def get_discount_three(self, shop_id: str, promotion: PromotionOffer):
        shop_cart_price = 0
        shop_cart_amount = 0

        for product in self.cart[shop_id]:
            quantity = self.cart[shop_id][product]["quantity"]
            if self.cart[shop_id][product].get("offer_price"):
                price = self.cart[shop_id][product]["offer_price"]
            else:
                price = int(get_object_or_404(Offer, product_id=product,
                                              shop_id=shop_id).price)
            shop_cart_price += quantity * price
            shop_cart_amount += quantity

        if shop_cart_price >= promotion.discount_type_value:
            for product in self.cart[shop_id]:
                self.cart[shop_id][product].setdefault("discount",
                                                       {promotion.id: 0})

                if promotion.discount_decimals != 0:
                    self.cart[shop_id][product]["discount"][
                        str(promotion.id)] = (
                        round(float(promotion.discount_decimals // shop_cart_amount, 2))
                    )

                else:
                    if self.cart[shop_id][product].get("offer_price"):
                        price = self.cart[shop_id][product]["offer_price"]
                    else:
                        price = int(get_object_or_404(Offer, product=product,
                                                      shop_id=shop_id).price)
                    self.cart[shop_id][product]["discount"][
                        str(promotion.id)] = int(
                        round(float(price * promotion.discount_percentage / 100), 2)
                    )

        else:
            for product in self.cart[shop_id]:
                self.cart[shop_id][product]["discount"][str(promotion.id)] = 0

    def get_discount_four(self, shop_id: str, promotion: PromotionOffer):
        shop_cart_amount = 0

        for product in self.cart[shop_id]:
            self.cart[shop_id][product].setdefault("discount",
                                                   {promotion.id: 0})
            quantity = self.cart[shop_id][product]["quantity"]
            shop_cart_amount += quantity

        if shop_cart_amount >= promotion.discount_type_value:
            for product in self.cart[shop_id]:

                if promotion.discount_decimals != 0:
                    self.cart[shop_id][product]["discount"][
                        str(promotion.id)] = (
                        round(float(promotion.discount_decimals / shop_cart_amount, 2))
                    )

                else:
                    price = self.cart[shop_id][product]["offer_price"]
                    self.cart[shop_id][product]["discount"][
                        str(promotion.id)] = (
                        round(float(price * (100 - promotion.discount_percentage) / 100, 2))
                    )

        else:
            for product in self.cart[shop_id]:
                self.cart[shop_id][product]["discount"][str(promotion.id)] = 0

    def get_discount_five(self, shop_id: str, product_id: str, promotion):
        flag = True
        for product in self.cart[shop_id]:
            if get_product_category_id(
                    product) == promotion.discount_type_value:
                flag = False

                if promotion.discount_decimals != 0:
                    self.cart[shop_id][product_id]["discount"][
                        str(promotion.id)] = round(float(promotion.discount_decimals), 2)
                    break

                else:
                    price = self.cart[shop_id][product_id]["price"]
                    self.cart[shop_id][product_id]["discount"][
                        str(promotion.id)] = (
                        round(float(price * (100 - promotion.discount_percentage) / 100, 2))
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
        for shop in self.cart:
            for product in self.cart[shop]:

                if self.cart[shop][product].get("final_price") and self.cart[shop][product].get("final_price") > 0:
                    price = self.cart[shop][product]["final_price"]
                    amount = self.cart[shop][product]["quantity"]

                else:
                    price = get_product_price_by_shop(shop, product)
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
        except Exception:
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
                float(get_object_or_404(Offer, product=product, shop=shop).price), 2)

        self.cart[shop][product].setdefault("discount", {"0": 0})
        for discount in self.cart[shop][product]["discount"].values():
            self.cart[shop][product]["final_price"] -= round(float(discount), 2)
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

    def add(self, product_id: str, shop_id: str, quantity: int = 1, update_quantity: bool = False):
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


class OrderFormation:
    """Составление заказа"""

    @classmethod
    def get_data_from_cart(cls, shops: Dict) -> Dict:
        """Формирование данных из корзины"""
        data_products = []
        full_total_price = 0
        total_price = 0

        for products in shops.values():
            for product in products.values():
                product["discount"] = Decimal(str(sum(product.pop("discount").values())))

                # пока Никита не добавит в структуру корзины offer_id
                if product.get("offer_id") is None:
                    offer = (
                        Offer.objects.values("pk")
                        .filter(shop_id=int(product.get("shop_id")), product_id=int(product.get("product_id")))
                        .first()
                    )
                    product["offer_id"] = offer.get("pk")

                full_total_price += product.get("quantity", 1) * Decimal(str(product.get("offer_price")))
                total_price += product.get("quantity", 1) * Decimal(str(product.get("final_price")))
                data_products.append(product)

        delivery_id, total = cls._get_data_delivery(
            shop_cnt=len(shops), full_total_price=full_total_price, total_price=total_price
        )
        order = {"products": data_products, "delivery_id": delivery_id, "total": total}
        return order

    @staticmethod
    def _get_data_delivery(shop_cnt: int, full_total_price: Decimal, total_price: Decimal) -> Tuple[int, Dict]:
        """Формирования итоговых цен с учетом доставки"""
        delivery_key = ("normal", "express")
        delivery = Delivery.objects.order_by("-updated_at").first()
        total = {}

        for key in delivery_key:
            if key == delivery_key[0]:
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
    return get_object_or_404(Offer, shop_id=shop_id, product_id=product_id).amount


def get_offer_id(shop: int, product: int):
    return get_object_or_404(Offer, product=product, shop=shop).id


def get_product_category(product_id: str):
    return get_object_or_404(Product, id=product_id).category


def get_product_category_id(product_id: str):
    return get_object_or_404(Product, id=product_id).category.id
