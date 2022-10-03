from django.test import TestCase
from django.db import connection
from django.contrib.auth import get_user_model
from product.models import ProductCategory, Product, Manufacturer, Offer, Review
from shop.models import Shop
from order.models import Order, OrderOffer
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse

User = get_user_model()


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

    def test_product_list_in_context(self):
        resp = self.client.get(reverse('catalog-page'))
        self.assertEqual(resp.status_code, 200)
        context = resp.context
        self.assertIsNotNone(context.get('product_list'))


class CatalogByCategoryViewTest(TestCase):
    category = 'category'
    category_another = 'another'

    @classmethod
    def setUpTestData(cls):
        category = ProductCategory.objects.create(name=cls.category, slug=cls.category)
        category_an = ProductCategory.objects.create(name=cls.category_another, slug=cls.category_another)
        man = Manufacturer.objects.create(name='Manufacturer')
        Product.objects.create(name='product_1', limited=False, category=category, manufacturer=man)
        Product.objects.create(name='product_2', limited=False, category=category, manufacturer=man)
        Product.objects.create(name='product_2', limited=False, category=category_an, manufacturer=man)

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

    def test_product_list_in_context(self):
        resp = self.client.get(reverse('category-catalog-page', args=[self.category]))
        self.assertEqual(resp.status_code, 200)
        context = resp.context
        self.assertIsNotNone(context.get('product_list'))

    def test_only_product_from_category_in_context(self):
        resp = self.client.get(reverse('category-catalog-page', args=[self.category]))
        self.assertEqual(resp.status_code, 200)
        for product in resp.context['product_list']:
            self.assertEqual(self.category, product.category.name)


class CatalogViewsSorting(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = ProductCategory.objects.create(name='category', slug='category')
        man = Manufacturer.objects.create(name='Manufacturer')

        p1 = Product.objects.create(name='product_1', limited=False, category=category, manufacturer=man)
        p2 = Product.objects.create(name='product_2', limited=False, category=category, manufacturer=man)
        p3 = Product.objects.create(name='product_3', limited=False, category=category, manufacturer=man)

        user = User.objects.create_user(email="testabcd@abcdtest.net", password="qwerty")
        Review.objects.create(product=p1, user=user, text='text', rating=1)
        Review.objects.create(product=p2, user=user, text='text', rating=5)

        shop = Shop.objects.create(name='shop', description='description', phone='+71234567890', email='shop@shop.ru',
                                   address='address', user=user)

        offer1 = Offer.objects.create(shop=shop, product=p1, price=1000, amount=10)
        offer2 = Offer.objects.create(shop=shop, product=p1, price=2000, amount=10)
        offer3 = Offer.objects.create(shop=shop, product=p2, price=3000, amount=10)

        order = Order.objects.create(user=user, city='city', address='address',
                                     delivery_type=1, payment_type=1, status_type=1)

        OrderOffer.objects.create(order=order, offer=offer1, price=1000, amount=10)
        OrderOffer.objects.create(order=order, offer=offer3, price=1000, amount=1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        with connection.cursor() as cursor:
            # лучше выполнить такую команду
            # SELECT setval(pg_get_serial_sequence('"user_customuser"','id'), coalesce(max("id"), 1),
            # max("id") IS NOT null) FROM "user_customuser";
            cursor.execute("TRUNCATE user_customuser RESTART IDENTITY CASCADE")

    def test_sort_by_newness(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'new'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].created_at < products[1].created_at)

    def test_sort_by_newness_rever(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'new', 'reverse': True}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].created_at > products[1].created_at)

    def test_sort_by_price(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'price'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].min_price > products[1].min_price)

    def test_sort_by_price_reverse(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'price', 'reverse': True}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].min_price < products[1].min_price)

    def test_sort_by_rating(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'rating'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].rating > products[1].rating)

    def test_sort_by_rating_reverse(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'rating', 'reverse': True}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].rating < products[1].rating)

    def test_sort_by_popularity(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'popular'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].order_count > products[1].order_count)

    def test_sort_by_popularity_reverse(self):
        url = reverse('catalog-page')
        data = {'sort_by': 'popular', 'reverse': True}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        products = resp.context['product_list']
        self.assertTrue(products[0].order_count < products[1].order_count)


class CatalogViewsFilter(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = ProductCategory.objects.create(name='category', slug='category')
        man = Manufacturer.objects.create(name='Manufacturer')

        p1 = Product.objects.create(name='product_1', limited=False, category=category, manufacturer=man)
        p2 = Product.objects.create(name='product_2', limited=True, category=category, manufacturer=man)
        p3 = Product.objects.create(name='goods_3', limited=True, category=category, manufacturer=man)

        user = User.objects.create_user(email="testabcd@abcdtest.net", password="qwerty")

        shop = Shop.objects.create(name='shop', description='description', phone='+71234567890', email='shop@shop.ru',
                                   address='address', user=user)
        Shop.objects.create(name='store', description='description', phone='+71234567891',
                            email='store@shop.ru', address='address', user=user)

        Offer.objects.create(shop=shop, product=p1, price=1000, amount=10)
        Offer.objects.create(shop=shop, product=p2, price=2000, amount=10)
        Offer.objects.create(shop=shop, product=p3, price=3000, amount=0)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE user_customuser RESTART IDENTITY CASCADE")

    def test_filter_by_limited(self):
        url = reverse('catalog-page')
        data = {'fil_limit': 'on'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        for product in resp.context['product_list']:
            self.assertTrue(product.limited)

    def test_filter_by_price(self):
        min_price = 1500
        max_price = 2500
        url = reverse('catalog-page')
        data = {'fil_price': f'{min_price};{max_price}'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        for product in resp.context['product_list']:
            self.assertGreaterEqual(product.min_price, min_price)
            self.assertLessEqual(product.min_price, max_price)

    def test_filter_by_title(self):
        search_word = 'prod'
        url = reverse('catalog-page')
        data = {'fil_title': search_word}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        for product in resp.context['product_list']:
            self.assertIn(search_word, product.name)

    def test_filter_by_shop(self):
        shop = 'shop'
        url = reverse('catalog-page')
        data = {'fil_shop': shop}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        for product in resp.context['product_list']:
            self.assertIn(shop, product.shop.values_list('name', flat=True))

    def test_filter_by_actual(self):

        url = reverse('catalog-page')
        data = {'fil_actual': 'on'}
        resp = self.client.get(url, data)
        self.assertEqual(resp.status_code, 200)
        for product in resp.context['product_list']:
            self.assertGreater(product.rest, 0)
