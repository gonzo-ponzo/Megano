from django import template
from order.services import Cart
from django.conf import settings

register = template.Library()


@register.simple_tag()
def get_cart_len(request):
    cart = Cart(request)
    return len(cart)


@register.simple_tag()
def get_cart_price(request):
    cart = Cart(request)
    cart.refresh()

    return cart.get_total_price()


@register.simple_tag()
def get_compare_len(request):
    if request.session.get(settings.CACHE_KEY_COMPARISON):
        return len(request.session.get(settings.CACHE_KEY_COMPARISON))
    return 0
