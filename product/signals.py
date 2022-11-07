from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import ProductCategory, Product
from constance.signals import config_updated
from constance import config


signals = dict()


@receiver([post_save, post_delete], sender=ProductCategory)
def clear_cache_product_category_handler(sender, **kwargs):
    cache.delete(settings.CACHE_KEY_PRODUCT_CATEGORY)


@receiver(post_save, sender=Product)
def delete_cache(sender, **kwargs):
    cache_list = [
        "main_pic",
        "pics",
        "low_price",
        "top_price",
        "discount",
        "product_description",
        "property_dict",
        "offer_dict",
    ]
    for cache_key in cache_list:
        cache.delete(cache_key)


@receiver(config_updated)
def constance_updated(sender, key, old_value, new_value, **kwargs):
    signals[key] = {
        "old_value": old_value,
        "new_value": new_value
    }
    if key == "CLEAR_CACHE" and config.CLEAR_CACHE == "Yes":
        cache.clear()
        setattr(config, "CLEAR_CACHE", "No")
        for signal in signals:
            if signals[signal]["old_value"] is not None:
                setattr(config, signal, signals[signal]["new_value"])
