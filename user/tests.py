from django.contrib import auth
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class UserTestLoginExample(TestCase):
    """Примеры создания пользователей для использования в тестах"""

    def test_check_normal_registration(self):
        get_user_model().objects.create_user(email="test@e.mail", password="test_password")
        login = self.client.login(email="test@e.mail", password="test_password")

        self.assertTrue(login)

    def test_check_registration_with_raw_password(self):
        test_user = get_user_model().objects.create(email="test@e.mail", password="test_password")
        self.client.force_login(test_user)

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.email, "test@e.mail")


User = get_user_model()


def user_create(email="test@test.com"):
    email = email
    test_user = User.objects.create(
        email=email,
        first_name="test_f",
        last_name="test_l",
        role="Buyer"
    )
    return test_user


class UserRegisterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_create()

    def test_url_address_and_template(self):
        url = reverse("registration-page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/register.html")

    def test_registration_successful(self):
        url = reverse("registration-page")
        email = "test1_email@test.com"
        response = self.client.post(
            url,
            {
                "email": email,
                "password1": "test_password",
                "password2": "test_password",
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "middle_name": "test_middle_name",
                "phone": "111-111-11-11"
            }
        )
        self.assertRedirects(response, reverse("main-page"))
        self.assertEqual(User.objects.filter(email=email).count(), 1)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_registration_failed(self):
        url = reverse("registration-page")

        # ошибка пароля
        response = self.client.post(
            url,
            {
                "email": "test_email@test.com",
                "password1": "test_password",
                "password2": "other_test_password",
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "middle_name": "test_middle_name",
                "phone": "111-111-11-11"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Пароли не совпадают"))

        # пользователь уже существует
        response = self.client.post(
            url,
            {
                "email": "test@test.com",
                "password1": "test_password",
                "password2": "test_password",
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "middle_name": "test_middle_name",
                "phone": "111-111-11-11"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Пользователь с таким емейлом уже зарегистрирован"))

        # неверный формат номера телефона
        response = self.client.post(
            url,
            {
                "email": "test_email@test.com",
                "password1": "test_password",
                "password2": "test_password",
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "middle_name": "test_middle_name",
                "phone": "1111"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Номер телефона должен быть в формате  123-456-78-90"))


class UserLoginViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = user_create()
        user.set_password("test_password")
        user.save()

    def test_url_address_and_template(self):
        url = reverse("login-page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/login.html")

    def test_login_successful(self):
        url = reverse("login-page")
        response = self.client.post(url, {"username": "test@test.com", "password": "test_password"})
        self.assertRedirects(response, reverse("main-page"))
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_failed_wrong_password(self):
        url = reverse("login-page")
        response = self.client.post(url, {"username": "test@test.com", "password": "incorrect_test_password"})
        self.assertTrue(response.status_code, 200)
        self.assertContains(response, _("Данные не корректны. Пожалуйста, попробуйте еще раз."))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_login_failed_unregistered(self):
        url = reverse("login-page")
        response = self.client.post(url, {"username": "guest@test.com", "password": "test_password"})
        self.assertTrue(response.status_code, 200)
        self.assertContains(response, _("Данные не корректны. Пожалуйста, попробуйте еще раз."))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

