import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='auth'
        )
        cls.authorized_author_client = Client()
        cls.authorized_author_client.force_login(cls.author)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.form = PostForm()
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """При отправке поста с картинкой через форму
        PostForm создаётся запись в базе данных"""
        posts_before = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.id,
            'text': 'test_post',
            'image': uploaded,
        }
        posts_before = Post.objects.count()
        response = self.authorized_author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text'],
                image='posts/small.gif'
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_before + 1)
        self.assertRedirects(response, reverse('posts:profile',
                             args=[self.author.username]))

    def test_edit_post(self):
        """Проверка формы редактирования поста."""
        form_data = {
            'text': 'some_text',
            'group': self.group.pk,
        }
        posts_before = Post.objects.count()
        response = self.authorized_author_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        response_post = response.context.get('post')
        self.assertTrue(
            Post.objects.filter(
                group=form_data['group'],
                text=form_data['text'],
                author=self.author,
            ).exists()
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(),
                         posts_before)
        self.assertNotEqual(response_post.text, self.post.text)

    def test_new_user(self):
        """Проверка формы регистрации"""
        users_before = User.objects.count()
        User.objects.create(username='username')
        form_data = {
            'first_name': 'mister',
            'last_name': 'x',
            'username': 'username',
            'email': 'x@yandex.ru',
        }
        self.guest_client.post(reverse('users:signup'),
                               data=form_data,
                               follow=True)
        self.assertEqual(User.objects.count(), users_before + 1)

    def test_comment_only_for_auth(self):
        """После успешной отправки комментарий
        появляется на странице поста.
        Комментировать посты может
        только авторизованный пользователь"""

        comments_before = self.post.comments.count()
        commentform_data = {
            'text': 'комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=commentform_data,
            follow=True,
        )

        expected_redirect = str(reverse('users:login') + '?next='
                                + reverse('posts:add_comment',
                                          args=[self.post.id]))

        self.assertRedirects(response, expected_redirect)
        self.assertEqual(self.post.comments.count(), comments_before)
        response = self.authorized_author_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=commentform_data,
            follow=True,
        )
        self.assertEqual(self.post.comments.count(), comments_before + 1)
        last_comment = self.post.comments.last()
        self.assertEqual(last_comment.text, commentform_data['text'])

    def test_guest_client_could_not_create_comments(self):
        """Неавторизованный пользователь не может комментировать посты."""

        comments_before = self.post.comments.count()
        form_data = {
            'text': 'комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        expected_redirect = str(reverse('users:login') + '?next='
                                + reverse('posts:add_comment',
                                args=[self.post.id]))
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(self.post.comments.count(), comments_before)
