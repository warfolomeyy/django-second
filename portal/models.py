from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    full_name = models.CharField('ФИО', max_length=255)
    email = models.EmailField('Email', unique=True)
    consent = models.BooleanField('Согласие на обработку ПД', default=False)

    def __str__(self):
        return f'{self.username} ({self.full_name})'


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100, unique=True)

    def __str__(self):
        return self.name


class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    title = models.CharField('Название заявки', max_length=200)
    description = models.TextField('Описание')
    photo = models.ImageField('Фото помещения или план', upload_to='plans/')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')

    admin_comment = models.TextField('Комментарий администратора', blank=True, null=True)
    design_image = models.ImageField('Готовый дизайн', upload_to='designs/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title