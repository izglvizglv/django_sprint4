from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import PublishedModel


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        max_length=64,
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:20]


class Location(PublishedModel):
    title = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.title[:20]


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Post(PublishedModel):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        default=timezone.now,
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.'
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', 'title')
        default_related_name = 'posts'

    def __str__(self):
        return self.title[:20]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
