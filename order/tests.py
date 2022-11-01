from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.contrib import auth
from .models import Order, OrderOffer, Delivery
from product.models import ProductCategory, Product, Manufacturer, Offer
from shop.models import Shop
import random

User = get_user_model()


class OrderTest(TestCase):
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

        user = auth.get_user(self.client)
        cache_order_data = cache.get(f"{settings.CACHE_KEY_CHECKOUT}{user.id}")
        self.assertFalse(cache_order_data)
        self.assertFalse(user.cart)
        self.assertRedirects(response, reverse("main-page"))


class OrderHistoryTest(TestCase):
    __password = "password12345"
    __emails = "user1@test.com"
    __order_id = 1
    __history_orders_url = reverse("order:history-orders")
    __detail_order_url = reverse("order:history-order-detail", kwargs={"pk": __order_id})

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email=cls.__emails, password=cls.__password)
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
                user=user,
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
            order = Order(user=user, city=f"city{i}", address=f"address{i}", delivery=delivery)
            orders.append(order)
        Order.objects.bulk_create(orders)

        orders_offers = []
        offer_cnt = 0
        for order in orders:
            offer_cnt += 2
            for offer in random.sample(offers, offer_cnt):
                order_offer = OrderOffer(order=order, offer=offer, price=offer.price, amount=random.randint(1, 3))
                orders_offers.append(order_offer)
        OrderOffer.objects.bulk_create(orders_offers)

        cls.user = user

    def test_history_redirect_on_login_if_not_authorized(self):
        response = self.client.get(self.__history_orders_url)
        self.assertEqual(response.status_code, 302)

    def test_detail_redirect_on_login_not_authorized(self):
        response = self.client.get(self.__detail_order_url)
        self.assertEqual(response.status_code, 302)

    def test_history_if_authorized(self):
        self.client.login(email=self.__emails, password=self.__password)
        response = self.client.get(self.__history_orders_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "order/historyorder.html")

    def test_detail_if_authorized(self):
        self.client.login(email=self.__emails, password=self.__password)
        response = self.client.get(self.__detail_order_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "order/oneorder.html")

    def test_check_count_history_order(self):
        self.client.login(email=self.__emails, password=self.__password)
        order_cnt = Order.objects.filter(user=self.user).count()
        response = self.client.get(self.__history_orders_url)
        self.assertEqual(len(response.context["order_list"]), order_cnt)

    def test_check_count_product_in_order_detail(self):
        self.client.login(email=self.__emails, password=self.__password)
        offer_cnt = OrderOffer.objects.filter(order_id=self.__order_id).count()
        order = Order.objects.get(id=self.__order_id)
        response = self.client.get(self.__detail_order_url)
        self.assertEqual(response.context["order"], order)
        self.assertEqual(len(response.context["products"]), offer_cnt)
