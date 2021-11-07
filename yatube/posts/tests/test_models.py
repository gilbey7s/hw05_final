from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Заголовок тестовой задачи",
            slug="test-task",
            description="Тестовое описание ...",
        )

        cls.post = Post.objects.create(
            text="Тестовый текст",
            author=PostModelTest.user,
            group=cls.group,
        )

        cls.group_field_verboses = {
            "title": "Заголовок",
            "slug": "Id",
            "description": "Описание",
        }

        cls.group_field_help_text = {
            "title": "Как корабль назовешь...",
            "slug": "Id, но воспринимаемый человеком!",
            "description": "Кратко и поделу!",
        }

        cls.post_field_verboses = {
            "text": "Текст",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }

        cls.post_field_help_text = {
            "text": "Ты можешь поведать свою историю...",
            "group": "Выбери группу",
        }

    def test_group_verbose_name(self):
        """verbose_name в полях 'group_field_verboses' совпадает
        с ожидаемым."""
        for value, expected in PostModelTest.group_field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(value).verbose_name,
                    expected,
                    f"Значение в {value} не совпадает с ожидаемым",
                )

    def test_post_verbose_name(self):
        """verbose_name в полях 'post_field_verboses' совпадает
        с ожидаемым."""
        for value, expected in PostModelTest.post_field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).verbose_name,
                    expected,
                    f"Значение в {value} не совпадает с ожидаемым",
                )

    def test_group_help_text(self):
        """help_text в полях 'group_field_help_text' совпадает с ожидаемым."""
        for value, expected in PostModelTest.group_field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.group._meta.get_field(value).help_text,
                    expected,
                    f"Значение в {value} не совпадает с ожидаемым",
                )

    def test_post_help_text(self):
        """help_text в полях 'post_field_help_text' совпадает с ожидаемым."""
        for value, expected in PostModelTest.post_field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    PostModelTest.post._meta.get_field(value).help_text,
                    expected,
                    f"Значение в {value} не совпадает с ожидаемым",
                )

    def test_group_str(self):
        """__str__  group - это строка с содержимым group.title."""
        group = PostModelTest.group
        title = str(group)
        self.assertEqual(title, group.title, "Это не строка")

    def test_post_str(self):
        """__str__  post - это строка с содержимым post.text."""
        post = PostModelTest.post
        text = post.text
        self.assertEqual(str(post), text[:15], "Это не строка")
