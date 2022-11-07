import os
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.conf import settings

from jobs.services import one_shop_import
from product.models import ProductCategory, Manufacturer, Product, Offer
from shop.models import Shop

User = get_user_model()


@override_settings(IMPORT_INCOME="jobs/tests/import-data", MEDIA_ROOT="jobs/tests/media")
class TestCoreImport(TestCase):
    @classmethod
    def setUpTestData(cls):
        # должны быть - юзер, группа, предмет, категория, производитель, магазин
        user = User.objects.create_user(email="test@e.mail", password="test_password")
        group, _ = Group.objects.get_or_create(name="SHOP_owner")
        perm = Permission.objects.get(codename="view_product")
        group.permissions.add(perm)
        group.save()
        category = ProductCategory.objects.create(name='category', slug='category')
        man = Manufacturer.objects.create(name='Manufacturer')
        Product.objects.create(name='product_1', limited=False, category=category, manufacturer=man)
        Shop.objects.create(name='shop', description='description', phone='+71234567890',
                            email='shop@shop.ru', address='address', user=user)
        User.objects.create_user(email="test@test.mail", password="test_password")

    def test_ok_only_shop(self):
        # файл с данными для создания нового магазина; файл с данными для редактирования этого же магазина
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "ok_only_shop_1.json"))
        self.assertTrue(is_ok)
        self.assertIn("created", "".join(messages))
        user = User.objects.get(email="test@test.mail")
        self.assertTrue(user.is_staff)
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "ok_only_shop_2.json"))
        self.assertTrue(is_ok)
        self.assertIn("edited", "".join(messages))
        shop = Shop.objects.get(email="shop_4@shop.ru")
        self.assertEqual(shop.name, "Renamed shop")

    def test_ok_shop_without_logo(self):
        # файл с данными для создания нового магазина без логотипа
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "ok_only_shop_3.json"))
        self.assertTrue(is_ok)
        self.assertIn("created", "".join(messages))

    def test_error_shop(self):
        # недостающие данные при создании магазина; некорректные (несуществующий юзер) - при редактировании
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "ok_only_shop_2.json"))
        self.assertFalse(is_ok)
        self.assertIn("ERROR", "".join(messages))
        shop = Shop.objects.filter(email="shop_4@shop.ru").first()
        self.assertFalse(shop)
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "fail_edit_shop.json"))
        self.assertFalse(is_ok)
        self.assertIn("ERROR", "".join(messages))
        shop = Shop.objects.get(email="shop@shop.ru")
        self.assertNotEqual(shop.name, "Renamed shop")

    def test_warning_offers(self):
        # в данных ссылки на два предмета, один есть в базе, другого нет
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "warning_offers.json"))
        self.assertFalse(is_ok)
        self.assertIn("WARNING", "".join(messages))
        self.assertNotIn("ERROR", "".join(messages))
        shop = Shop.objects.get(email="shop@shop.ru")
        count_offers = Offer.objects.filter(shop=shop).count()
        self.assertEqual(count_offers, 1)

    def test_error_offers(self):
        # некорректные данные для оффера - минусовое количество, и цена с тремя знаками после запятой
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "error_offers.json"))
        self.assertFalse(is_ok)
        str_messages = "".join(messages)
        self.assertNotIn("WARNING", str_messages)
        self.assertIn("ERROR", str_messages)
        self.assertIn("-33", str_messages)
        self.assertIn("1523.077", str_messages)

    def test_ok_offers(self):
        is_ok, messages = one_shop_import(os.path.join(settings.IMPORT_INCOME, "ok_offers.json"))
        self.assertTrue(is_ok)
        shop = Shop.objects.get(email="shop@shop.ru")
        count_offers = Offer.objects.filter(shop=shop).count()
        self.assertEqual(count_offers, 1)

    def test_import_from_site_need_permission(self):
        pass  # TODO
