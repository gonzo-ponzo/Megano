from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

from product.models import ProductCategory, Product, Manufacturer, ProductView
from product.services import PopularCategory

User = get_user_model()


class TestPopularCategory(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(email="test@test.net", password="qwerty")
        man = Manufacturer.objects.create(name='Manufacturer')

        for i in range(1, 6):
            category = ProductCategory.objects.create(name=f'category_{i}', slug=f'category{i}')
            for p in range(i):
                product = Product.objects.create(name=f'product_{i}', limited=False,
                                                 category=category, manufacturer=man)
                ProductView.objects.create(user=user, product=product)

    def test_num_queries(self):
        self.assertNumQueries(1, PopularCategory.get_popular_category)

    def test_count_of_category(self):
        count = 3
        category = PopularCategory.get_cached()
        self.assertEqual(count, len(category))

    def test_category_sort_by_viewed_product(self):
        category = PopularCategory.get_cached()
        self.assertTrue(category[0].parameter > category[1].parameter > category[2].parameter)

    def test_correct_category(self):
        category = PopularCategory.get_cached()
        self.assertEqual('category_5', category[0].name)
        self.assertEqual('category_4', category[1].name)
        self.assertEqual('category_3', category[2].name)

    def test_get_in_cache(self):
        category = PopularCategory.get_cached()
        self.assertNumQueries(0, PopularCategory.get_cached)

    def test_key_in_cache(self):
        key = settings.CACHE_KEY_POPULAR_CATEGORY
        cache.delete(key)
        self.assertIsNone(cache.get(key))
        PopularCategory.get_cached()
        self.assertIsNotNone(cache.get(key))
