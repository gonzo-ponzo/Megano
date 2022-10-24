from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from .models import Shop

User = get_user_model()


class TestStaffRightForShopOwners(TestCase):
    @classmethod
    def setUpTestData(cls):
        group, fl = Group.objects.get_or_create(name="SHOP_owner")
        perm = Permission.objects.get(codename="view_product")
        group.permissions.add(perm)
        group.save()
        User.objects.create(email="user1@mail.mail")
        User.objects.create(email="user2@mail.mail")

    def test_check_add_rights_creation_shop(self):
        user1 = User.objects.get(email="user1@mail.mail")
        Shop.objects.create(name="blabla", user=user1)
        user1.refresh_from_db()
        self.assertTrue(user1.is_staff)

    def test_check_change_rights_edit_shop(self):
        user1 = User.objects.get(email="user1@mail.mail")
        user2 = User.objects.get(email="user2@mail.mail")
        shop = Shop.objects.create(name="blabla", user=user1)
        shop.user = user2
        shop.save()
        user1.refresh_from_db()
        self.assertFalse(user1.is_staff)
        user2.refresh_from_db()
        self.assertTrue(user2.is_staff)
