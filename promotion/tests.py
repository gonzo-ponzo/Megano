from django.conf import settings
from django.urls import reverse
from product.tests.test_product_category import ProductCategoryCacheCleanTest
from .models import Banner
from product.models import Product
from user.tests import CacheTestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class BannerCacheCleanTest(ProductCategoryCacheCleanTest):
    _model = Banner
    _cache_key = settings.CACHE_KEY_BANNER

    @classmethod
    def _create_object(cls):
        product = Product.objects.first()
        cls._model.objects.create(name="new", product=product, image="")


class PromotionOfferTest(CacheTestCase):
    fixtures = [
        "product_category.json",
        "manufacturer.json",
        "product.json",
        "product_offer.json",
        "user.json",
        "shop.json",
        "discount_type.json",
        "promotion_offer.json",
        "promotion_offer-offer"
    ]
    __password = "testpassword"
    __email = "testuser@test.com"

    def setUp(self):
        user = User.objects.create_user(email=self.__email, password=self.__password)
        user.save()
        self.client.login(email=self.__email, password=self.__password)

    def tearDown(self) -> None:
        self.client.get("/order/cart-clear/")

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/promotion/")
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("promotion-list-page"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "promotion/promotions.html")

    def test_promotion_type_1(self):
        self.client.get("/order/cart-add/1/1/")
        user = User.objects.filter(email=self.__email).first()
        final_price = user.cart["1"]["1"]["final_price"]
        self.assertEqual(final_price, 94000)

    def test_promotion_type_2(self):
        for _ in range(3):
            self.client.get("/order/cart-add/3/1/")
        user = User.objects.filter(email=self.__email).first()
        final_price = user.cart["1"]["3"]["final_price"]

        self.assertEqual(final_price, 56000)

    def test_promotion_type_3(self):
        for _ in range(2):
            self.client.get("/order/cart-add/1/1/")
        self.client.get("/order/cart-add/2/1/")

        user = User.objects.filter(email=self.__email).first()
        sum_discount = 0
        for item in user.cart["1"].values():
            sum_discount += item["discount"]["3"]

        self.assertEqual(sum_discount, 9000)

    def test_promotion_type_4(self):
        for _ in range(4):
            self.client.get("/order/cart-add/3/1/")
        self.client.get("/order/cart-add/1/1/")

        user = User.objects.filter(email=self.__email).first()
        sum_discount = 0
        for item in user.cart["1"].values():
            sum_discount += item["discount"]["4"] * item["quantity"]

        self.assertEqual(sum_discount, 50000)

    def test_promotion_type_5(self):
        self.client.get("/order/cart-add/2/2/")
        self.client.get("/order/cart-add/1/2/")

        user = User.objects.filter(email=self.__email).first()
        final_price = user.cart["2"]["2"]["final_price"]

        self.assertEqual(final_price, 68000)

    def test_cart_price_discount_from_different_shops(self):
        self.client.get("/order/cart-add/1/1/")
        for _ in range(3):
            self.client.get("/order/cart-add/2/2/")

        user = User.objects.filter(email=self.__email).first()
        result = user.cart["1"]["1"]["discount"].get("3", None)

        self.assertEqual(result, 0)

    def test_cart_amounth_discount_from_different_shops(self):
        for _ in range(4):
            self.client.get("/order/cart-add/1/1/")
        self.client.get("/order/cart-add/2/2/")

        user = User.objects.filter(email=self.__email).first()
        result = user.cart["1"]["1"]["discount"].get("4", None)

        self.assertEqual(result, 0)
