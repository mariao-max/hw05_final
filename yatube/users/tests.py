from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_exist_at_desired_location(self):
        """Страницы  доступны любому пользователю."""
        URLS = ['/auth/signup/', '/auth/logout/',
                '/auth/login/', '/auth/password_reset/']
        for url in URLS:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'users/signup.html': '/auth/signup/',
            'users/login.html': '/auth/login/',
            'users/logged_out.html': '/auth/logout/',
            'users/password_reset_form.html': '/auth/password_reset/',
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
