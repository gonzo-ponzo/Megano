from django.urls import reverse
from django.conf import settings
from user.tests import CacheTestCase


class TestI18n(CacheTestCase):

    def test_language_select_exists_at_desired_location(self):
        resp = self.client.post('/i18n/setlang/', follow=True)
        self.assertEqual(resp.status_code//100, 2, msg='Код ответа HTTP должен быть 2хх - успешно')

    def test_language_select_accessible_by_name(self):
        resp = self.client.post(reverse('set_language'), follow=True)
        self.assertEqual(resp.status_code//100, 2, msg='Код ответа HTTP должен быть 2хх - успешно')

    def test_response_in_required_language(self):
        for lang in 'en', 'ru':
            with self.subTest(language=lang):
                resp = self.client.post(reverse('set_language'), data={'language': lang}, follow=True)
                self.assertEqual(lang, resp.headers.get('Content-Language'))

    def test_correct_language_response_when_language_in_header(self):
        for lang in 'en', 'ru':
            with self.subTest(language=lang):
                resp = self.client.get(reverse('main-page'), HTTP_ACCEPT_LANGUAGE=lang)
                self.assertEqual(lang, resp.headers.get('Content-Language'))

    def test_language_using_cookie(self):
        for lang in 'en', 'ru':
            with self.subTest(language=lang):
                self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: lang})
                resp = self.client.get(reverse('main-page'))
                self.assertEqual(lang, resp.headers.get('Content-Language'))

    def test_relly_content_in_ru(self):
        resp = self.client.get(reverse('main-page'), HTTP_ACCEPT_LANGUAGE='ru')
        self.assertContains(resp, 'каталог', status_code=200)

    def test_relly_content_in_en(self):
        resp = self.client.get(reverse('main-page'), HTTP_ACCEPT_LANGUAGE='en')
        self.assertContains(resp, 'catalog', status_code=200)
