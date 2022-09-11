from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import ProductCategory


@receiver([post_save, post_delete], sender=ProductCategory)
def clear_cache_product_category_post_save_or_delete_handler(sender, **kwargs):
    cache.delete(settings.CACHE_KEY_PRODUCT_CATEGORY)
