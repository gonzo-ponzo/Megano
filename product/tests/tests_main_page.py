from django.test import TestCase
from django.contrib.auth import get_user_model
from product.models import ProductCategory, Product, Manufacturer, Offer
from shop.models import Shop
from order.models import Order, OrderOffer
from django.urls import reverse

User = get_user_model()


class MainPageView(TestCase):

    @classmethod
    def setUpTestData(cls):
        category = ProductCategory.objects.create(name='category', slug='category')
        man = Manufacturer.objects.create(name='Manufacturer')

        p1 = Product.objects.create(name='product_111', limited=False, category=category, manufacturer=man)
        p2 = Product.objects.create(name='product_222', limited=True, category=category, manufacturer=man)
        p3 = Product.objects.create(name='product_333', limited=True, category=category, manufacturer=man)

        user = User.objects.create_user(email="testabcd@abcdtest.net", password="qwerty")
        shop = Shop.objects.create(name='shop', description='description', phone='+71234567890', email='shop@shop.ru',
                                   address='address', user=user)
        offer1 = Offer.objects.create(shop=shop, product=p1, price=1000, amount=10)
        Offer.objects.create(shop=shop, product=p2, price=1000, amount=10)
        Offer.objects.create(shop=shop, product=p3, price=1000, amount=10)
        order = Order.objects.create(user=user, city='city', address='address',
                                     delivery_type=1, payment_type=1, status_type=1)

        OrderOffer.objects.create(order=order, offer=offer1, price=1000, amount=5)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('main-page'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('main-page'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'product/index.html')
