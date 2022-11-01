from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import Banner


@receiver([post_save, post_delete], sender=Banner)
def clear_cache_banner_handler(sender, **kwargs):
    cache.delete(settings.CACHE_KEY_BANNER)
