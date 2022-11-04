from django.urls import reverse
from django.contrib.auth import get_user_model
from product.models import ProductCategory, Product, Manufacturer, Offer
from promotion.models import DiscountType, PromotionOffer
from product.services import DailyOffer
from shop.models import Shop
from order.models import Order, OrderOffer, Delivery
from user.tests import CacheTestCase

User = get_user_model()


class MainPageView(CacheTestCase):

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
        discount_type = DiscountType.objects.create(description='description')
        active_promotion = PromotionOffer.objects.create(name='active_promo', description='description',
                                                         discount_type_value=1, is_active=True,
                                                         discount_type_id=discount_type)
        non_active_promotion = PromotionOffer.objects.create(name='non_active_promo', description='description',
                                                             discount_type_value=1, is_active=False,
                                                             discount_type_id=discount_type)
        for i in range(32):
            p_lim = Product.objects.create(name=f'product_lim_{i}', limited=True, category=category, manufacturer=man)
            p = Product.objects.create(name=f'product_{i}', limited=False, category=category, manufacturer=man)
            of1 = Offer.objects.create(shop=shop, product=p_lim, price=1000, amount=10)
            of2 = Offer.objects.create(shop=shop, product=p, price=1000, amount=10)
            non_active_promotion.offer.add(of1)
            active_promotion.offer.add(of2)

        offer1 = Offer.objects.create(shop=shop, product=p1, price=1000, amount=10)
        Offer.objects.create(shop=shop, product=p2, price=1000, amount=10)
        Offer.objects.create(shop=shop, product=p3, price=1000, amount=10)
        delivery = Delivery.objects.create(price=200, express_price=500, sum_order=2000)
        order = Order.objects.create(user=user, city='city', address='address',
                                     delivery_type=1, payment_type=1, status_type=1,
                                     delivery=delivery)

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

    def test_need_context_in_response(self):
        resp = self.client.get(reverse('main-page'))
        context = resp.context
        self.assertIsNotNone(context.get('banners'))
        self.assertIsNotNone(context.get('top_product'))
        self.assertIsNotNone(context.get('daily_offer'))
        self.assertIsNotNone(context.get('limited_product'))
        self.assertIsNotNone(context.get('hot_product'))
        self.assertIsNotNone(context.get('popular_category'))

    def test_top_product_count(self):
        top_product_count = 8
        resp = self.client.get(reverse('main-page'))
        top_product = resp.context['top_product']
        self.assertEqual(len(top_product), top_product_count)

    def test_limited_product_count(self):
        limited_product_count = 16
        resp = self.client.get(reverse('main-page'))
        limited_product = resp.context['limited_product']
        self.assertEqual(len(limited_product), limited_product_count)

    def test_hot_product_count(self):
        hot_product_count = 9
        resp = self.client.get(reverse('main-page'))
        hot_product = resp.context['hot_product']
        self.assertEqual(len(hot_product), hot_product_count)

    def test_sort_top_product_by_popularity(self):
        resp = self.client.get(reverse('main-page'))
        top_product = resp.context['top_product']
        self.assertTrue(top_product[0].order_count > top_product[1].order_count)

    def test_if_limited_product_relly_limited(self):
        resp = self.client.get(reverse('main-page'))
        limited_product = resp.context['limited_product']
        for product in limited_product:
            self.assertTrue(product.limited)

    def test_daily_offer_not_in_limited_product(self):
        daily_offer_id = DailyOffer().product_id
        resp = self.client.get(reverse('main-page'))
        limited_product = resp.context['limited_product']
        for product in limited_product:
            self.assertNotEqual(daily_offer_id, product.id)

    def test_hot_product_is_relly_hot_and_promo_active(self):
        resp = self.client.get(reverse('main-page'))
        hot_product = resp.context['hot_product']
        for product in hot_product:
            promo = PromotionOffer.objects.filter(is_active=True).filter(offer__product_id=product.id)
            self.assertGreaterEqual(promo.count(), 1)
