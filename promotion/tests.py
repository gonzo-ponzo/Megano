from django.test import TestCase
from django.conf import settings
from product.tests.test_product_category import ProductCategoryCacheCleanTest
from .models import Banner
from product.models import Product
from django.urls import reverse


class BannerCacheCleanTest(ProductCategoryCacheCleanTest):
    _model = Banner
    _cache_key = settings.CACHE_KEY_BANNER

    @classmethod
    def _create_object(cls):
        product = Product.objects.first()
        cls._model.objects.create(name="new", product=product, image="")


class PromotionOfferTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get("/promotion/")
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse("promotion-list-page"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "promotion/promotions.html")
