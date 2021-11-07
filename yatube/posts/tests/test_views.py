import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post


User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="user")

        cls.group = Group.objects.create(
            title="Заголовок тестовой задачи",
            slug="test-slug",
            description="Тестовое описание ...",
        )

        cls.group_two = Group.objects.create(
            title="Заголовок тестовой задачи two",
            slug="test-slug-two",
            description="Тестовое описание two...",
        )

        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        test_image = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        cls.post = Post.objects.create(
            text="Текст",
            author=User.objects.get(username="user"),
            group=cls.group,
            image=test_image,
        )

    def assertPostsEqual(self, expected_post, actual_post):
        self.assertEqual(expected_post.text, actual_post.text)
        self.assertEqual(expected_post.author, actual_post.author)
        self.assertEqual(expected_post.group, actual_post.group)
        self.assertEqual(expected_post.image, actual_post.image)

    def createPost(text_for_post):
        post = Post.objects.create(
            text=text_for_post,
            author=User.objects.get(username="user"),
            group=PagesTests.group,
        )
        return post

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PagesTests.user)
        self.guest_client = Client()

        self.templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_posts", kwargs={"slug": PagesTests.group.slug}
            ),
            "posts/post_create.html": reverse("posts:post_create"),
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech"),
        }
        self.urls_reverse = [
            "index",
        ]

    def test_pages_use_correct_template(self):
        """URL-адреса "self.templates_pages_names" использует
        соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f"URL-адрес {reverse_name} использует другой шаблон",
                )

    def test_index_page_show_correct_context(self):
        """Шаблон 'index' сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        self.assertPostsEqual(PagesTests.post, first_object)

    def test_group_page_show_correct_context(self):
        """Шаблон 'group_list' сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:group_posts", kwargs={"slug": PagesTests.group.slug}
            )
        )
        first_object = response.context["page_obj"][0]
        self.assertPostsEqual(PagesTests.post, first_object)

    def test_new_post_page_show_correct_context(self):
        """Шаблон 'create' сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_index_shows_new_post(self):
        """На главной появляется пост"""
        post = PagesTests.createPost(text_for_post="index")
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response.context["page_obj"][0], post)

    def test_group_1_shows_new_post(self):
        """На странице group появляется пост"""
        post = PagesTests.createPost(text_for_post="group")
        response = self.authorized_client.get(
            reverse(
                "posts:group_posts", kwargs={"slug": PagesTests.group.slug}
            )
        )
        self.assertEqual(response.context["page_obj"][0], post)

    def test_profile_new_post(self):
        """На странице profile появляется пост"""
        post = PagesTests.createPost(text_for_post="profile")
        response = self.authorized_client.get(
            reverse(
                "posts:profile", kwargs={"username": PagesTests.user.username}
            )
        )
        self.assertEqual(response.context["page_obj"][0], post)

    def test_group_2_shows_not_post(self):
        """На странице group_two пост не появляется"""
        PagesTests.createPost(text_for_post="non_group_2")
        response = self.authorized_client.get(
            reverse(
                "posts:group_posts",
                kwargs={"slug": PagesTests.group_two.slug},
            )
        )
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit",
                kwargs={
                    "post_id": PagesTests.post.id,
                },
            )
        )
        self.assertEqual(response.context["post"], self.post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:profile", kwargs={"username": PagesTests.user.username}
            )
        )
        self.assertEqual(response.context["author"], PagesTests.user)
        self.assertPostsEqual(
            response.context["page_obj"][0], PagesTests.post
        )

    def test_cache_index_page(self):
        """Запись остаётся"""
        response = self.authorized_client.get(reverse("posts:index"))
        content = response.content
        Post.objects.create(
            text="Пост для проверки кеша",
            author=self.user,
        )
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(content, response.content)
        cache.clear()
        response = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(content, response.content)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="user")
        cls.client = Client()
        cls.client.force_login(cls.user)
        for p in range(11):
            Post.objects.bulk_create(
                [
                    Post(
                        text="Тестовый пост",
                        author=cls.user,
                    )
                ]
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_first_page_containse_ten_records(self):
        response = self.client.get(reverse("posts:index"))
        self.assertEqual(
            len(response.context.get("page_obj").object_list), 10
        )

    def test_second_page_containse_three_records(self):
        response = self.client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context.get("page_obj").object_list), 1)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.follower = User.objects.create_user(username="follower")
        cls.author = User.objects.create_user(username="author")

        cls.post = Post.objects.create(
            text="Пост для подписки", author=cls.author
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_follow(self):
        """Авторизованный пользователь может подписываться"""
        self.authorized_follower.get(
            reverse("posts:profile_follow", args={self.author.username})
        )
        follow_count = Follow.objects.filter(
            user=self.follower.id, author=self.author.id
        ).count()
        self.assertEqual(follow_count, 1)

    def test_unfollow(self):
        """Авторизованный пользователь может отписываться"""
        Follow.objects.create(user=self.follower, author=self.author)
        self.authorized_follower.get(
            reverse("posts:profile_unfollow", args={self.author.username})
        )
        follow_count = Follow.objects.filter(
            user=self.follower.id, author=self.author.id
        ).count()
        self.assertEqual(follow_count, 0)

    def test_post_in_follower_index(self):
        """Новая запись автора появляется у подписчиков."""
        Follow.objects.create(user=self.follower, author=self.author)
        response = self.authorized_follower.get(reverse("posts:follow_index"))
        post = response.context["page_obj"][0]
        self.assertEqual(post.text, self.post.text)

    def test_post_not_in_user_index(self):
        """Новая запись не появляется у неподписанных авторов"""
        response = self.authorized_user.get(reverse("posts:follow_index"))
        posts = response.context["page_obj"]
        self.assertNotIn(self.post, posts)
