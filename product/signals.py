from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import ProductCategory, Product


def clear_product_category_cache():
    cache.delete(settings.CACHE_NAME_PRODUCT_CATEGORY)


@receiver(post_delete, sender=ProductCategory)
def product_category_post_delete_handler(sender, **kwargs):
    clear_product_category_cache()


@receiver(post_save, sender=ProductCategory)
def product_category_post_save_handler(sender, **kwargs):
    clear_product_category_cache()


@receiver(post_save, sender=Product)
def delete_cache(sender, **kwargs):
    cache_list = ['main_pic', 'pics', 'low_price', 'top_price', 'discount',
                  'product_description', 'property_dict', 'offer_dict']
    for cache_key in cache_list:
        cache.delete(cache_key)
