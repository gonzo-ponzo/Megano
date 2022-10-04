import os
from django.contrib import auth
from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.files import File


class UserTestLoginExample(TestCase):
    """Примеры создания пользователей для использования в тестах"""
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(email="test@e.mail", password="test_password")

    def test_check_normal_registration(self):
        login = self.client.login(email="test@e.mail", password="test_password")

        self.assertTrue(login)

    def test_check_registration_without_password(self):
        test_user = get_user_model().objects.get(email="test@e.mail")
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
        last_name="test_l"
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
                "phone": "+7(926)111-11-11"
            }
        )
        self.assertRedirects(response, reverse("main-page"))
        self.assertEqual(User.objects.filter(email=email).count(), 1)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_registration_with_avatar_successful(self):
        url = reverse("registration-page")
        email = "email@test.com"
        file_source = "user/pics/test_avatar.jpg"
        with open(file_source, 'rb') as fp:
            response = self.client.post(
                url,
                {
                    "email": email,
                    "password1": "test_password",
                    "password2": "test_password",
                    "first_name": "test_first_name",
                    "last_name": "test_last_name",
                    "middle_name": "test_middle_name",
                    "phone": "+7(926)111-11-11",
                    "avatar": fp
                }
            )
            self.assertRedirects(response, reverse("main-page"))
        self.assertEqual(User.objects.filter(email=email).count(), 1)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(os.path.basename(user.avatar.name), "test_avatar.jpg")
        avatar = user.avatar
        if os.path.isfile(avatar.path):
            os.remove(avatar.path)

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
                "phone": "+7(926)111-11-11"
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
                "phone": "+7(926)111-11-11"
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
        self.assertContains(response, _("Enter a valid phone number"))

        # телефон не указан
        response = self.client.post(
            url,
            {
                "email": "test_email@test.com",
                "password1": "test_password",
                "password2": "test_password",
                "first_name": "test_first_name",
                "last_name": "test_last_name",
                "middle_name": "test_middle_name"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("required"))


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


class UserLogoutViewTest(TestCase):
    def test_success_logout(self):
        get_user_model().objects.create_user(email="test@e.mail", password="test_password")
        self.client.login(email="test@e.mail", password="test_password")
        url = reverse("logout")
        response = self.client.get(url)
        self.assertRedirects(response, reverse("main-page"))
        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)


class UserPageNotAuthenticatedTest(TestCase):
    def test_userpages_not_allowed(self):
        names = ['account', 'profile', 'orders_history', 'views_history']
        url_login = reverse('login-page')
        for name in names:
            url = reverse(name)
            response = self.client.get(url)
            self.assertRedirects(response, f'{url_login}?next={url}')


class UserPagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(email="test@e.mail", password="test_password")

    def setUp(self):
        self.client.login(email="test@e.mail", password="test_password")

    def test_userpage(self):
        names = ['profile', 'orders_history', 'views_history']
        url = reverse('account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/account.html")
        for name in names:
            self.assertContains(response, reverse(name))
        # TODO проверить наличие остальных разделов

    def test_userpage_update_get(self):
        names = ['account', 'orders_history', 'views_history']
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/profile.html")
        for name in names:
            self.assertContains(response, reverse(name))


class AccountTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create(email="test@e.mail", first_name="Hassan",
                                        last_name="Abdurahman", middle_name="ibn Hottab")
        get_user_model().objects.create(email="test@em.ail", first_name="Name",
                                        last_name="Family")
        file_source = 'user/pics/test_avatar.jpg'
        with open(file_source, 'rb') as fp:
            get_user_model().objects.create(email="test@ema.il",
                                            avatar=File(fp, name=os.path.basename(fp.name)))

    @classmethod
    def tearDownClass(cls):
        avatar = get_user_model().objects.get(email="test@ema.il").avatar
        if os.path.isfile(avatar.path):
            os.remove(avatar.path)
        super(AccountTest, cls).tearDownClass()  # Call parent last

    def test_fio(self):
        url = reverse('account')
        user1 = get_user_model().objects.get(email="test@e.mail")
        self.client.force_login(user1)
        response = self.client.get(url)
        self.assertContains(response, user1.get_fio)
        user2 = get_user_model().objects.get(email="test@em.ail")
        self.client.force_login(user2)
        response = self.client.get(url)
        self.assertContains(response, user2.get_fio)

    def test_avatar(self):
        url = reverse('account')
        user3 = get_user_model().objects.get(email="test@ema.il")
        self.client.force_login(user3)
        response = self.client.get(url)
        self.assertContains(response, user3.avatar.url)


class UpdateProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(email="test@e.mail", password="password")

    def setUp(self):
        self.client.login(email="test@e.mail", password="password")

    def test_post_simple_update(self):
        # только фамилию-имя, телефон, емейл
        url = reverse("profile")
        form = {"email": "pupkin@mail.mail", "phone": "+79262221133",
                "fio": "Pupkin Basil Mirmirovich", "password1": "", "password2": ""}
        response = self.client.post(url, form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Профиль успешно сохранен"))
        user = auth.get_user(self.client)
        self.assertEqual(user.email, "pupkin@mail.mail")
        self.assertEqual(user.phone, "+79262221133")
        self.assertEqual(user.first_name, "Basil")
        self.assertEqual(user.last_name, "Pupkin")
        self.assertEqual(user.middle_name, "Mirmirovich")

    def test_invalid_form(self):
        # невалидный номер телефона, невалидный емейл, меньше двух слов в поле фамилия-имя
        url = reverse("profile")
        form = {"email": "pupkin@mailmail", "phone": "+7926222113", "fio": "Pupkin", "password1": "", "password2": ""}
        response = self.client.post(url, form)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("Профиль успешно сохранен"))
        self.assertContains(response, _("Введите правильный адрес электронной почты."))
        self.assertContains(response, _("Enter a valid phone number"))
        self.assertContains(response, _("Нужно написать Фамилию Имя"))
        user = auth.get_user(self.client)
        self.assertNotEqual(user.email, "pupkin@mailmail")
        self.assertNotEqual(user.phone, "+7926222113")
        self.assertNotEqual(user.last_name, "Pupkin")

    def test_change_password(self):
        # форма с двумя введенными паролями
        url = reverse("profile")
        form = {"email": "test@e.mail", "phone": "+79262221133", "fio": "Pupkin Basil",
                "password1": "new_password", "password2": "new_password"}
        response = self.client.post(url, form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Профиль успешно сохранен"))
        self.assertFalse(authenticate(email="test@e.mail", password="password"))
        self.assertTrue(authenticate(email="test@e.mail", password="new_password"))

    def test_fail_change_password(self):
        # введен один пароль, несовпадающие пароли
        url = reverse("profile")
        form = {"email": "test@e.mail", "phone": "+79262221133", "fio": "Pupkin Basil",
                "password1": "new_password", "password2": ""}
        response = self.client.post(url, form)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("Профиль успешно сохранен"))
        self.assertTrue(authenticate(email="test@e.mail", password="password"))
        self.assertFalse(authenticate(email="test@e.mail", password="new_password"))
        form = {"email": "test@e.mail", "phone": "+79262221133", "fio": "Pupkin Basil",
                "password1": "new_password", "password2": "another_new_password"}
        response = self.client.post(url, form)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, _("Профиль успешно сохранен"))
        self.assertTrue(authenticate(email="test@e.mail", password="password"))
        self.assertFalse(authenticate(email="test@e.mail", password="new_password"))

    def test_change_avatar(self):
        # форма редактирования с аватаром - должен появиться новый,
        # повторный запрос с новой картинкой - файл должен замениться на новый
        url = reverse("profile")
        file_source = "user/pics/test_avatar.jpg"
        with open(file_source, 'rb') as fp:
            form = {"email": "pupkin@mail.mail", "phone": "+79262221133", "fio": "Pupkin Basil",
                    "password1": "", "password2": "", "avatar": fp}
            response = self.client.post(url, form)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Профиль успешно сохранен"))
        user = auth.get_user(self.client)
        self.assertEqual(os.path.basename(user.avatar.name), "test_avatar.jpg")
        last_avatar = user.avatar
        file_source = "user/pics/test_avatar.png"
        with open(file_source, 'rb') as fp:
            form = {"email": "pupkin@mail.mail", "phone": "+79262221133", "fio": "Pupkin Basil",
                    "password1": "", "password2": "", "avatar": fp}
            response = self.client.post(url, form)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Профиль успешно сохранен"))
        user = auth.get_user(self.client)
        self.assertEqual(os.path.basename(user.avatar.name), "test_avatar.png")
        self.assertFalse(os.path.isfile(last_avatar.path))
        avatar = user.avatar
        if os.path.isfile(avatar.path):
            os.remove(avatar.path)
