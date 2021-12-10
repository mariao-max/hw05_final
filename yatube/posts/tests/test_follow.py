import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

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
    content_type='image/gif')
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.author = User.objects.create_user(
            username='author'
        )
        cls.authorized_client = Client()
        cls.user = User.objects.create_user(
            username='user'
        )
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.post = Post.objects.create(
            text='test_post',
            group=cls.group,
            author=cls.author,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_follow(self):
        """Авторизованный пользователь может
        подписываться на других пользователей"""
        URL = reverse('posts:profile_follow', args=[self.author.username])
        follows_before = Follow.objects.count()
        self.authorized_client.get(URL, follow=True)
        self.assertEqual(Follow.objects.count(), follows_before + 1)
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.author).exists())

    def test_unfollow(self):
        """Авторизованный пользователь может удалять
        пользователей из подписок."""
        URL = reverse('posts:profile_unfollow', args=[self.author.username])
        Follow.objects.create(user=self.user, author=self.author)
        follows_before = Follow.objects.count()
        self.authorized_client.get(URL, follow=True)
        self.assertEqual(Follow.objects.count(), follows_before - 1)
        self.assertFalse(Follow.objects.filter(user=self.user,
                                               author=self.author).exists())

    def check_context(self, response_post):
        self.assertEqual(response_post.author, self.post.author)
        self.assertEqual(response_post.group, self.group)
        self.assertEqual(response_post.text, self.post.text)
        self.assertEqual(response_post.image, self.post.image)

    def test_post_on_the_follower_page(self):
        """Новая запись пользователя появляется в ленте
        тех, кто подписан """
        Follow.objects.create(user=self.user, author=self.author)
        URL = reverse('posts:follow_index')
        response = self.authorized_client.get(URL)
        response_post = response.context['page_obj'][0]
        self.check_context(response_post)

    def test_no_post_on_the_unfollower_page(self):
        """Новая запись пользователя не появляется в ленте
        тех, кто не подписан """
        URL = reverse('posts:follow_index')
        response = self.authorized_client.get(URL)
        content = response.context['page_obj']
        self.assertNotIn(self.post, content)
