from django import template
from product.models import ProductCategory

register = template.Library()


@register.simple_tag()
def get_product_categories():
    return ProductCategory.with_active_products_count().filter(products_cumulative_count__gt=0)
