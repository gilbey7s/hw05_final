from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):

    title = models.CharField(
        verbose_name="Заголовок",
        max_length=200,
        help_text="Как корабль назовешь...",
    )
    slug = models.SlugField(
        verbose_name="Id",
        unique=True,
        help_text="Id, но воспринимаемый человеком!",
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Кратко и поделу!",
    )

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(
        verbose_name="Текст",
        help_text="Ты можешь поведать свою историю...",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выбери группу",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    created = models.DateTimeField("date published", auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return self.text


class Follow(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="follower"
            )
        ]
