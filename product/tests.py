from django.test import TestCase
from product.models import ProductCategory
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse


class ProductCategoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        parent_name = "parent"
        parent = ProductCategory.objects.create(name=parent_name, slug=parent_name)
        for i in range(3):
            child_name = f"child{i}"
            ProductCategory.objects.create(name=child_name, slug=child_name, parent=parent)

    def test_check_delete_parent_with_child(self):
        category = ProductCategory.objects
        category.get(name="child1").delete()
        self.assertEquals(category.count(), 3)
        category.filter(name="parent").delete()
        self.assertEquals(category.count(), 0)


class ProductCategoryCacheCleanTest(TestCase):
    fixtures = ["product_category.json", "manufacturer.json", "product.json", "banner.json"]
    _model = ProductCategory
    _cache_key = settings.CACHE_KEY_PRODUCT_CATEGORY

    @classmethod
    def _create_object(cls):
        cls._model.objects.create(name="new")

    @classmethod
    def _update_object(cls):
        obj = cls._model.objects.first()
        obj.name = "new"
        obj.save()

    @classmethod
    def _delete_object(cls):
        cls._model.objects.first().delete()

    def test_cache_clean_model(self):
        funcs = (self._create_object, self._update_object, self._delete_object)
        for func in funcs:
            self.client.get(reverse("main-page"))
            self.assertTrue(cache.get(self._cache_key))
            func()
            self.assertFalse(cache.get(self._cache_key))


class CatalogViewTest(TestCase):

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('catalog-page'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('catalog-page'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'product/catalog.html')

class CatalogByCategryViewTest(TestCase):

    category = 'category'

    @classmethod
    def setUpTestData(cls):
        ProductCategory.objects.create(name=cls.category, slug=cls.category)

    def test_view_url_exists_at_desired_location(self):

        resp = self.client.get(f'/catalog/{self.category}/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('category-catalog-page', args=[self.category]))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('category-catalog-page', args=[self.category]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'product/catalog.html')

    def test_404_for_non_exist_category(self):
        resp = self.client.get(reverse('category-catalog-page', args=['non_exist_category']))
        self.assertEqual(resp.status_code, 404)
