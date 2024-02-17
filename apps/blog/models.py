from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField

from apps.stdimage2 import StdImageField


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):  # email
        if not username:
            raise ValueError("Пользватель должен иметь логин!")

        user = self.model(
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email=None):
        user = self.create_user(
            username=username,
            password=password,
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractUser):
    is_moderator = models.BooleanField(default=False)
    objects = MyUserManager()


class Category(models.Model):
    for iso, _ in settings.LANGUAGES:
        locals()[f"name_{iso}"] = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, max_length=100)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'{self.slug}'


class Tags(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, blank=True, max_length=100)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return f'{self.slug}'


class News(models.Model):
    STATUS_CHOICES = (
        ('moderation', 'IN-MODERATION'),
        ('published', 'PUBLISHED'),
        ('rejected', 'REJECTED')
    )
    for iso, _ in settings.LANGUAGES:
        locals()[f"title_{iso}"] = models.CharField(max_length=255)
        locals()[f"brief_{iso}"] = models.TextField(max_length=1000)
        locals()[f"description_{iso}"] = HTMLField(max_length=10000)
        locals()[f"tg_image_{iso}"] = models.ImageField(upload_to="news_images/%Y/%m/%d/", blank=True, null=True)
    draft = models.BooleanField(default=True)
    video = models.FileField(upload_to='news_videos/%Y/%m/%d/', blank=True, null=True)
    pub_date = models.DateTimeField(default=timezone.now)
    picture = StdImageField(upload_to="news_images/%Y/%m/%d/", variations={
        'large': (1200, 600),
        'medium': (600, 300),
        'small': (300, 200),
        'thumb': (40, 30, True), })
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="news")
    status = models.CharField(choices=STATUS_CHOICES, default='moderation', max_length=100)
    view_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True,
                                   related_name="news_created_by")
    updated_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True,
                                   related_name="news_updated_by")
    slug = models.SlugField(null=True, max_length=255)
    tags = models.ManyToManyField(Tags, )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return f'{self.title_uz}'


class TinyMCEPicture(models.Model):
    original = models.ImageField(verbose_name="original", max_length=255)
    converted = models.ImageField(verbose_name="converted", max_length=255)

    def __str__(self):
        return self.original.slug + ', ' + self.converted.slug
