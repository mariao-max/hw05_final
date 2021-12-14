from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
URL_INDEX = reverse('posts:index')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test-slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='some_text',
            group=cls.group,
            author=cls.author
        )

    def test_cache_on_index_page_exists(self):
        """Кэширование данных на главной странице существует."""
        response = self.authorized_client.get(URL_INDEX)
        cached_response_content = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get(URL_INDEX)
        cached_content_after_delete = response.content
        self.assertEqual(
            cached_response_content,
            cached_content_after_delete
        )

    def test_cache_on_index_page_updates(self):
        """Данные на странице обновляются."""
        response = self.authorized_client.get(URL_INDEX)
        cached_response_content = response.content
        cache.clear()
        Post.objects.create(
            text='some_text',
            group=self.group,
            author=self.author
        )
        response = self.authorized_client.get(URL_INDEX)
        self.assertNotEqual(
            cached_response_content,
            response.content
        )
