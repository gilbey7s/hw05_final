from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username="user_author")
        cls.user_not_author = User.objects.create_user(
            username="user_non_author"
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client_non_author = Client()
        cls.authorized_client.force_login(cls.user_author)
        cls.authorized_client_non_author.force_login(cls.user_not_author)
        cls.group = Group.objects.create(
            title="Название - Тест",
            slug="slug-test",
            description="Описание - Тест",
        )
        cls.post = Post.objects.create(
            text="Текст - Тест",
            group=cls.group,
            author=cls.user_author,
        )

    def setUp(self):

        self.urls_access_anonymous = {
            "/": 200,
            f"/group/{PostsUrlsTests.group.slug}/": 200,
            f"/profile/{PostsUrlsTests.user_author}/": 200,
            f"/posts/{PostsUrlsTests.post.id}/": 200,
        }

        self.urls_access_avtorized = {
            "/create/": 200,
            f"/posts/{PostsUrlsTests.post.id}/edit/": 200,
        }

        self.urls_redirect_post_non_author = {
            f"/posts/{PostsUrlsTests.post.id}/edit/":
                f"/posts/{PostsUrlsTests.post.id}/",
        }

        self.templates = {
            "/": "posts/index.html",
            f"/group/{PostsUrlsTests.group.slug}/": "posts/group_list.html",
            f"/profile/{PostsUrlsTests.user_author}/": "posts/profile.html",
            f"/posts/{PostsUrlsTests.post.id}/": "posts/post_detail.html",
            "/create/": "posts/post_create.html",
            f"/posts/{PostsUrlsTests.post.id}/edit/": "posts/post_create.html",
        }

        self.urls_redirect = {
            f"/posts/{PostsUrlsTests.post.id}/edit/":
                f"/auth/login/?next=/posts/{PostsUrlsTests.post.id}/edit/",
            "/create/": "/auth/login/?next=/create/",
        }

    def test_urls_exists_at_desired_location(self):
        """Страницы 'self.urls_access_anonymous' доступны
        любому пользователю."""

        for value, expected in self.urls_access_anonymous.items():
            with self.subTest():
                response = PostsUrlsTests.guest_client.get(value)
                self.assertEqual(
                    response.status_code,
                    expected,
                    f" страница - {value} не доступна",
                )

    def test_new_url_exists_at_desired_location_authorized(self):
        """Страницы 'self.urls_access_avtorized' доступны
        авторизованному пользователю."""
        for value, expected in self.urls_access_avtorized.items():
            with self.subTest():
                response = self.authorized_client.get(value)
                self.assertEqual(
                    response.status_code,
                    expected,
                    f"страница - {value} не доступна",
                )

    def test_edit_post_not_available_authorized_non_author(self):
        """Страницы 'self.urls_access_avtorized_non_author' не
        доступны авторизованному пользователю не автору поста."""
        for url, redirect_url in self.urls_redirect_post_non_author.items():
            with self.subTest():
                response = self.authorized_client_non_author.get(url)
                self.assertRedirects(response, (redirect_url))

    def test_urls_uses_correct_template(self):
        """URL-адреса в 'self.templates' используют
        соответствующие шаблоны."""
        for reverse_name, template in self.templates.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    f"Для url-адреса '{ reverse_name }' неверный шаблон!",
                )

    def test_redirects_urls_non_authorized(self):
        """Страницы по адресам из 'self.urls_redirect' перенаправляют
        анонимного пользователя."""
        for url, redirect_url in self.urls_redirect.items():
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, (redirect_url))

    def test_404(self):
        """Возвращается ошибка 404"""
        response = self.guest_client.get("/miss/")
        self.assertEqual(response.status_code, 404)
