from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.contrib import auth
from django.db.models import F

from .models import Order, OrderOffer, Delivery
from product.models import ProductCategory, Product, Manufacturer, Offer
from shop.models import Shop
from .tasks import update_order_after_payment
from user.tests import CacheTestCase

import random
from typing import List
from unittest import mock

User = get_user_model()


class MockResponsePayment:
    """Mock для Payment API"""

    def __init__(self, method: str, status_code: int, order_number: int):
        self.method = method
        self.status_code = status_code
        self.order_number = order_number

    def json(self):
        response = {}
        if self.method == "post":
            if self.status_code == 201:
                response = {"order_number": self.order_number, "status": 0, "status_text": "Новый заказ"}
            elif self.status_code == 400:
                response = {"error": "Некорректные входные данные"}
        elif self.method == "get":
            if self.status_code == 200:
                response = {"order_number": self.order_number, "status": 1, "status_text": "Успешно оплачено"}
            elif self.status_code == 400:
                response = {"error": "Счет не найден"}
        return response


class OrderTest(CacheTestCase):
    fixtures = [
        "product_category.json",
        "manufacturer.json",
        "product.json",
        "user.json",
        "shop.json",
        "offer_test_order.json",
        "delivery.json",
    ]
    __url = "order:create-order"
    __password = "password12345"
    __emails = ("user1@test.com", "user2@test.com")
    __cart = {
        "2": {
            "1": {
                "limits": 4,
                "shop_id": "2",
                "discount": {"0": 0, "1": 6000.0, "3": 0},
                "offer_id": 1,
                "quantity": 1,
                "shop_name": "i-store",
                "product_id": "1",
                "final_price": 84000.99,
                "offer_price": 90000.99,
                "product_name": "Смартфон Apple iPhone 13 128GB (темная ночь)",
                "product_image": "product/2022/09/13/iphone-13-pro.png",
            }
        }
    }

    def setUp(self):
        User.objects.create_user(email=self.__emails[0], password=self.__password)
        user = User.objects.create_user(email=self.__emails[1], password=self.__password)
        user.cart = self.__cart
        user.save()

    def tearDown(self) -> None:
        cache.clear()

    def test_http403_if_cart_empty_and_logout(self):
        response = self.client.get(reverse(self.__url))
        self.assertEqual(response.status_code, 403)

    def test_http403_if_cart_empty_and_login(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        response = self.client.get(reverse(self.__url))
        self.assertEqual(response.status_code, 403)

    def test_http200_and_cache_if_cart_full_and_login(self):
        self.client.login(email=self.__emails[1], password=self.__password)
        response = self.client.get(reverse(self.__url))
        self.assertEqual(response.status_code, 200)
        user = auth.get_user(self.client)
        cache_order_data = cache.get(f"{settings.CACHE_KEY_CHECKOUT}{user.id}")
        self.assertTrue(cache_order_data)

    def test_post_order(self):
        data = {"delivery_type": 1, "city": "Минск", "address": "пр. Притыцкого 105-30", "payment_type": 2}

        self.client.login(email=self.__emails[1], password=self.__password)
        self.client.get(reverse(self.__url))
        response = self.client.post(reverse(self.__url), data=data)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderOffer.objects.count(), 1)
        order = Order.objects.first()
        order_cache = cache.get(settings.CACHE_KEY_PAYMENT_ORDER.format(user_id=order.user_id, order_id=order.id))
        self.assertTrue(order_cache)
        self.assertEqual(order.id, order_cache.get("order").id)
        self.assertRedirects(response, reverse("order:payment-order", kwargs={"order_id": order.id}))

        user = auth.get_user(self.client)
        cache_order_data = cache.get(f"{settings.CACHE_KEY_CHECKOUT}{user.id}")
        self.assertFalse(cache_order_data)
        self.assertFalse(user.cart)


class OrderHistoryTest(CacheTestCase):
    __password = "password12345"
    __emails = ["user1@test.com", "user2@test.com"]
    __order_id = 1
    __history_orders_url = reverse("order:history-orders")
    __detail_order_url = reverse("order:history-order-detail", kwargs={"pk": __order_id})

    @classmethod
    def setUpTestData(cls):
        cls.users = adding_data_to_tables(cls.__emails, cls.__password)

    def tearDown(self):
        cache.clear()

    def test_history_redirect_on_login_if_not_authorized(self):
        response = self.client.get(self.__history_orders_url)
        self.assertEqual(response.status_code, 302)

    def test_detail_redirect_on_login_not_authorized(self):
        response = self.client.get(self.__detail_order_url)
        self.assertEqual(response.status_code, 302)

    def test_history_if_authorized(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        response = self.client.get(self.__history_orders_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "order/historyorder.html")

    def test_detail_if_authorized(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        response = self.client.get(self.__detail_order_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "order/oneorder.html")

    def test_check_count_history_order(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        order_cnt = Order.objects.filter(user=self.users[0]).count()
        response = self.client.get(self.__history_orders_url)
        self.assertEqual(len(response.context["order_list"]), order_cnt)

    def test_check_count_product_in_order_detail(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        offer_cnt = OrderOffer.objects.filter(order_id=self.__order_id).count()
        order = Order.objects.get(id=self.__order_id)
        response = self.client.get(self.__detail_order_url)
        self.assertEqual(response.context["order"], order)
        self.assertEqual(len(response.context["products"]), offer_cnt)

    def test_if_redirect_not_your_order(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        order = Order.objects.filter(user=self.users[1]).first()
        response = self.client.get(reverse("order:history-order-detail", kwargs={"pk": order.id}))
        self.assertEqual(response.status_code, 404)

    def test_order_detail_post_payment_and_redirect(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        order = Order.objects.filter(user=self.users[0]).first()
        data = {"payment_type": 2}
        response = self.client.post(reverse("order:history-order-detail", kwargs={"pk": order.id}), data)
        new_order = Order.objects.get(pk=order.id)
        self.assertEqual(data.get("payment_type"), new_order.payment_type)
        self.assertRedirects(response, reverse("order:payment-order", kwargs={"order_id": order.id}))


class OrderPaymentTest(CacheTestCase):
    __password = "password12345"
    __emails = ["user1@test.com", "user2@test.com"]
    __payment_name_url = "order:payment-order"
    __payment_url = reverse(__payment_name_url, kwargs={"order_id": 1})

    @classmethod
    def setUpTestData(cls):
        cls.users = adding_data_to_tables(cls.__emails, cls.__password)

    def tearDown(self) -> None:
        cache.clear()

    def test_if_not_authorized_payment_http404(self):
        response = self.client.get(self.__payment_url)
        self.assertEqual(response.status_code, 404)

    def test_if_authorized_and_your_order(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        order = Order.objects.filter(user=self.users[0]).first()
        response = self.client.get(reverse(self.__payment_name_url, kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 200)

    def test_if_authorized_and_not_your_order(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        order = Order.objects.filter(user=self.users[1]).first()
        response = self.client.get(reverse(self.__payment_name_url, kwargs={"order_id": order.id}))
        self.assertEqual(response.status_code, 404)

    def test_if_authorized_and_order_status(self):
        self.client.login(email=self.__emails[0], password=self.__password)
        order = Order.objects.filter(user=self.users[0]).first()
        for status in range(1, 5):
            if status > 1:
                order.status_type = status
                order.save()
            response = self.client.get(reverse(self.__payment_name_url, kwargs={"order_id": order.id}))
            if status == 3:
                self.assertEqual(response.status_code, 403)
            else:
                self.assertEqual(response.status_code, 200)
            cache.clear()

    @mock.patch("order.tasks.update_order_after_payment.apply_async")
    @mock.patch("requests.post")
    def test_post_payment_and_true_result(self, mocked, call_task):
        self.client.login(email=self.__emails[1], password=self.__password)
        order = Order.objects.filter(user=self.users[1]).first()
        call_task.return_value = None
        mocked.return_value = MockResponsePayment(method="post", status_code=201, order_number=order.id)
        url = reverse(self.__payment_name_url, kwargs={"order_id": order.id})
        data = {"card_number": "1233 3434"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("order:history-order-detail", kwargs={"pk": order.id}))

    @mock.patch("order.tasks.update_order_after_payment.apply_async")
    @mock.patch("requests.post")
    def test_post_payment_and_false_result(self, mocked, call_task):
        self.client.login(email=self.__emails[1], password=self.__password)
        order = Order.objects.filter(user=self.users[1]).first()
        call_task.return_value = None
        mocked.return_value = MockResponsePayment(method="post", status_code=400, order_number=order.id)
        url = reverse(self.__payment_name_url, kwargs={"order_id": order.id})
        data = {"card_number": "1233 34jhj34"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    @mock.patch("requests.get")
    def test_update_order_task_true_result(self, requests_get):
        order = Order.objects.first()
        offer_old = (
            OrderOffer.objects.select_related("offer")
            .values("offer_id", offer_amount=F("offer__amount"))
            .filter(order=order)
        )
        offer_old = [i for i in offer_old]
        offer = (
            OrderOffer.objects.select_related("offer")
            .values("offer_id")
            .annotate(offer_amount=F("offer__amount") - F("amount"))
            .filter(order=order)
        )
        offer = [i for i in offer]
        self.assertTrue(offer_old != offer)

        requests_get.return_value = MockResponsePayment(method="get", status_code=200, order_number=order.id)
        result = update_order_after_payment(order.id)
        offer_new = (
            OrderOffer.objects.select_related("offer")
            .values("offer_id", offer_amount=F("offer__amount"))
            .filter(order=order)
        )
        offer_new = [i for i in offer_new]
        self.assertEqual(offer_new, offer)
        self.assertTrue(result.startswith("Good"))


def adding_data_to_tables(emails: List, password: str) -> List:
    users = []
    for email in emails:
        user = User.objects.create_user(email=email, password=password)
        users.append(user)
    category = ProductCategory.objects.create(name="category", slug="category")
    manufacturer = Manufacturer.objects.create(name="Manufacturer")
    delivery = Delivery.objects.create(price=200, express_price=500, sum_order=2000)

    products = []
    for i in range(5):
        product = Product(name=f"product{1}", category=category, manufacturer=manufacturer)
        products.append(product)
    Product.objects.bulk_create(products)

    shops = []
    for i in range(2):
        shop = Shop(
            name=f"shop{1}",
            description="description",
            phone=f"++37533758659{i}",
            email=f"shop{i}@test.com",
            address="address",
            user=users[0],
        )
        shops.append(shop)
    Shop.objects.bulk_create(shops)

    offers = []
    for shop in shops:
        for product in products:
            offer = Offer(
                shop=shop, product=product, price=random.randint(50000, 200000), amount=random.randint(5, 10)
            )
            offers.append(offer)
    Offer.objects.bulk_create(offers)

    orders = []
    for i in range(3):
        user = users[0] if i % 2 == 0 else users[1]
        order = Order(user=user, city=f"city{i}", address=f"address{i}", delivery=delivery)
        orders.append(order)
    Order.objects.bulk_create(orders)

    orders_offers = []
    offer_cnt = 0
    for order in orders:
        offer_cnt += 2
        for offer in random.sample(offers, offer_cnt):
            order_offer = OrderOffer(
                order=order, offer=offer, price=offer.price, amount=random.randint(1, 3), discount=0
            )
            orders_offers.append(order_offer)
    OrderOffer.objects.bulk_create(orders_offers)

    return users
