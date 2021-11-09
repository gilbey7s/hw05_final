import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="user")
        cls.group = Group.objects.create(
            title="Тестовая группа", description="Тест", slug="test-group"
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group
        )
        cls.comment = {
            'text': 'Комментарий'
        }
        cls.comment_second = {
            'text': 'Еще комментарий'
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)
        self.guest_client = Client()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_new_post_created_from_form_data(self):
        """Создает пост"""
        posts_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        test_image = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif",
        )
        form_data = {
            "text": "Текст из формы",
            "group": PostFormTests.group.id,
            "image": test_image,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user.username}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                group=PostFormTests.group.id,
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Редактируется пост"""
        post = Post.objects.create(
            text="Текст",
            author=self.user,
        )
        edit_post_data = {
            "text": "Текст изменился",
        }
        self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": post.id}),
            data=edit_post_data,
            follow=True,
        )
        post.refresh_from_db()
        self.assertEqual(post.text, edit_post_data["text"])


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Форма комментария создает запись."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[self.post.id]))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий', post=CommentFormTests.post.id
            ).exists()
        )

    def test_comment_guest_client(self):
        """Гость не может комментировать посты."""
        url = f'/auth/login/?next=/posts/{CommentFormTests.post.id}/comment/'
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertRedirects(response, url)
