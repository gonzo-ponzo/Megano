from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.contrib import auth
from .models import Order, OrderOffer

User = get_user_model()


class OrderTest(TestCase):
    fixtures = ["product_category.json", "manufacturer.json", "product.json",
                "user.json", "shop.json", "offer_test_order.json", "delivery.json"]
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
                "product_image": "product/2022/09/13/iphone-13-pro.png"
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
        data = {"delivery_type": 1, 'city': "Минск",
                "address": "пр. Притыцкого 105-30", "payment_type": 2}

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
