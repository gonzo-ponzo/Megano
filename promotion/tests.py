from django.test import TestCase  # noqa: F401
from django.conf import settings
from product.tests import ProductCategoryCacheCleanTest
from .models import Banner
from product.models import Product


class BannerCacheCleanTest(ProductCategoryCacheCleanTest):
    _model = Banner
    _cache_key = settings.CACHE_KEY_BANNER

    @classmethod
    def _create_object(cls):
        product = Product.objects.first()
        cls._model.objects.create(name="new", product=product, image="")
