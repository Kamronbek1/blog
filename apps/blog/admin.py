from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe

from api.v1.blog.utils import parse_and_download_images
from .models import News, Currency, Account, TinyMCEPicture, Tags, Category


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = 'title_uz', 'brief_uz', 'slug',
    readonly_fields = ['id', 'created_by', 'updated_by', 'view_count', 'get_tg_image_uz', 'get_tg_image_uz_to',
                       'get_picture']
    prepopulated_fields = {'slug': ('title_uz',)}

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = self.model.objects.get(id=obj.id)
            obj.updated_by = request.user
            for iso, _ in settings.LANGUAGES:
                description = getattr(old_obj, f"description_{iso}", None)
                if getattr(obj, f"description_{iso}", None) != description:
                    new_desc = parse_and_download_images(getattr(obj, f"description_{iso}", None))
                    setattr(obj, f"description_{iso}", new_desc)
        else:
            obj.created_by = request.user
            for iso, _ in settings.LANGUAGES:
                new_desc = parse_and_download_images(getattr(obj, f"description_{iso}", None))
                setattr(obj, f"description_{iso}", new_desc)
        obj.save()

    @staticmethod
    def get_tg_image_uz(obj):
        if obj.tg_image_uz:
            return mark_safe(f'<img src="{obj.tg_image_uz.url}" width="150" height="150" />')

    @staticmethod
    def get_tg_image_uz_to(obj):
        image_uz_to = getattr(obj, 'tg_image_uz-to', None)
        if image_uz_to:
            return mark_safe(f'<img src="{image_uz_to.url}" width="150" height="150" />')

    @staticmethod
    def get_picture(obj):
        if obj.picture:
            return mark_safe(f'<img src="{obj.picture.url}" width="150" height="150" />')


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = 'name',


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'name_uz', 'name_uz-to'
    prepopulated_fields = {'slug': ('name_uz',)}


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = 'username',


@admin.register(TinyMCEPicture)
class TinyMCEPictureAdmin(admin.ModelAdmin):
    list_display = 'id', 'original', 'converted', 'get_converted'

    @staticmethod
    def get_converted(obj):
        if obj.converted:
            return mark_safe(f'<img src="{obj.converted.url}" width="150" height="150" />')
