from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import User

User = get_user_model()


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user)
    if request.user == user:
        show_edit_link = True
    else:
        show_edit_link = False
    return render(request, 'blog/profile.html', {
        'profile_user': user,
        'posts': posts,
        'show_edit_link': show_edit_link,
    })


class Category(models.Model):

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField(
        "Описание",
        blank=True
    )
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        ordering = ['title']


class Location(models.Model):
    name = models.CharField(
        "Название места",
        max_length=256
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"
        ordering = ['name']


class Post(models.Model):

    title = models.CharField(
        'Заголовок',
        max_length=256
    )

    text = models.TextField(
        'Текст'
    )

    pub_date = models.DateTimeField(
        'Дата и время публикации',
        default=timezone.now,
        help_text=(
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        )
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post',
        verbose_name='Автор публикации'
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='post',
        null=True,
        blank=True,
        verbose_name='Местоположение'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='post',
        null=True,
        blank=False,
        verbose_name='Категория'
    )

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )

    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    image = models.ImageField(upload_to='post_images/',
    blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
