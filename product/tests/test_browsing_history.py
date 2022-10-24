from django.test import TestCase
from django.contrib.auth import get_user_model
from product.models import ProductCategory, Product, Manufacturer, ProductView
from promotion.models import DiscountType, PromotionOffer
from product.services import BrowsingHistory
from shop.models import Shop
from order.models import Order, OrderOffer, Delivery
from django.urls import reverse

User = get_user_model()


class TestBrowsingHistory(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = ProductCategory.objects.create(name='category', slug='category')
        man = Manufacturer.objects.create(name='Manufacturer')

        p1 = Product.objects.create(name='product_111', limited=False, category=category, manufacturer=man)
        p2 = Product.objects.create(name='product_222', limited=True, category=category, manufacturer=man)
        p3 = Product.objects.create(name='product_333', limited=True, category=category, manufacturer=man)
        user = User.objects.create_user(email='test@test.net', password='qwerty')

    def test_add_product_to_history_for_authorized_user(self):
        user = User.objects.get(email='test@test.net')
        user_history = BrowsingHistory(user)
        self.client.force_login(user)
        products = Product.objects.all()
        self.assertEqual(0, user_history.count)
        for product in products[0:2]:
            self.client.get(reverse('product-page', args=[product.id]))
        self.assertEqual(2, user_history.count)

    def test_not_add_product_to_history_for_unauthorized_user(self):
        user = User.objects.get(email='test@test.net')
        user_history = BrowsingHistory(user)
        products = Product.objects.all()
        self.assertEqual(0, user_history.count)
        for product in products:
            self.client.get(reverse('product-page', args=[product.id]))
        self.assertEqual(0, user_history.count)

    def test_right_order_product_in_history(self):
        user = User.objects.get(email='test@test.net')
        user_history = BrowsingHistory(user)
        self.client.force_login(user)
        products = Product.objects.all().order_by('-id')
        for product in products:
            self.client.get(reverse('product-page', args=[product.id]))
        history_id = [item.id for item in user_history.get_history()]
        self.assertEqual(history_id, sorted(history_id))
        # смотрим последний продукт еще раз, он должен стать первым
        last_id = history_id[-1]
        self.client.get(reverse('product-page', args=[last_id]))
        self.assertEqual(last_id, user_history.get_history().first().id)
