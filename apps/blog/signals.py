from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Tags


@receiver(post_save, sender=Tags, dispatch_uid="update_slug")
def update_tag(sender, instance, update_fields, **kwargs):
    if not update_fields == {'slug'}:
        instance.slug = slugify(instance.name) + '-' + str(instance.id)
        print(instance)
        instance.save(update_fields=['slug'])
