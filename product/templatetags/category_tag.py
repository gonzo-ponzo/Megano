from django import template
from django.core.cache import cache
from django.conf import settings
from product.models import ProductCategory

register = template.Library()


@register.simple_tag()
def get_product_categories():
    category = cache.get_or_set(
        settings.CACHE_KEY_PRODUCT_CATEGORY,
        ProductCategory.with_active_products_count().filter(products_cumulative_count__gt=0),
        settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_PRODUCT_CATEGORY),
    )
    return category


@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    dict_ = context['request'].GET.copy()
    dict_[field] = value
    return dict_.urlencode()
