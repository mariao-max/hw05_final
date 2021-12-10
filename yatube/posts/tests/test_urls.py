from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='auth'
        )
        cls.authorized_author_client = Client()
        cls.authorized_author_client.force_login(cls.author)
        cls.not_author = User.objects.create_user(
            username='test_not_author'
        )
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.not_author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author,
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/posts/1/comment/': 'posts/post_detail.html',
            '/follow/': 'posts/index.html'
        }

    def test_pages_exist_at_desired_location(self):
        """Страницы /,profile, group, posts
        доступны любому пользователю."""
        urls = ['/', '/profile/auth/',
                '/posts/1/', '/group/test_slug/']
        for url in urls:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit_auth_author(self):
        """Страница /posts/1/edit/ доступна
         автору поста.
        """
        response = self.authorized_author_client.get(
            '/posts/1/edit/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_only_for_authorized(self):
        """Страницы /posts/1/comment/, /create/, /follow/, 
        доступны авторизованному пользователю."""
        urls = ['/create/','/follow/', '/posts/1/comment/']
        for url in urls:
            response = self.authorized_not_author_client.get(url, follow=True)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404(self):
        """При запросе несуществующей страницы сервер возвращает код 404."""
        response = self.guest_client.get('/about/one/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)          


    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """Страницы по адресу /create/, /follow/, /profile/author/follow/, 
        /profile/author/unfollow/, /posts/1/edit/ перенаправят анонимного
        пользователя на страницу логина.
        """
        dict = {'/create/': '/auth/login/?next=/create/',
                '/follow/': '/auth/login/?next=/follow/',
                '/profile/leo/follow/': '/auth/login/?next=/profile/leo/follow/',
                '/profile/leo/unfollow/': '/auth/login/?next=/profile/leo/unfollow/',
                '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/'
        }
        for url, redirect in dict.items():
            with self.subTest(url=url):
                response=self.guest_client.get(url, follow=True)
                self.assertRedirects(response,redirect)


    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_not_author_client.get(url)
                self.assertTemplateUsed(response, template)

    

    