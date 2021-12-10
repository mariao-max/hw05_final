from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст более 15 символов',
        )

    def test_Post_model_has_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_post = self.post.text[:15]
        str_post = str(self.post)
        self.assertEqual(expected_post, str_post)

    def test_Group_model_has_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        expected_group = self.group.title
        str_group = str(self.group)
        self.assertEqual(expected_group, str_group)
