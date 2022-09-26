from django import template
from order.cart import Cart
from django.conf import settings

register = template.Library()


@register.simple_tag()
def get_cart_len(request):
    return len(Cart(request))


@register.simple_tag()
def get_cart_price(request):
    return Cart(request).get_total_price()


@register.simple_tag()
def get_compare_len(request):
    return len(request.session.get(settings.CACHE_KEY_COMPARISON))
