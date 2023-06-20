from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from core.models import PublishedModel
from .constants import MAX_LENGTH_256, MAX_LENGTH_64


User = get_user_model()


class Category(PublishedModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        max_length=MAX_LENGTH_64,
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:20]


class Location(PublishedModel):
    title = models.CharField('Название места', max_length=MAX_LENGTH_256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.title[:20]


class Post(PublishedModel):
    title = models.CharField('Заголовок', max_length=MAX_LENGTH_256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        default=timezone.now,
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.')
    image = models.ImageField('Фото', upload_to='birthdays_images', blank=True)
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
        verbose_name='Post'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:20]
