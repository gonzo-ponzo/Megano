from django import template
from order.services import Cart

register = template.Library()


@register.simple_tag()
def get_cart_len(request):
    return len(Cart(request))


@register.simple_tag()
def get_cart_price(request):
    return Cart(request).get_total_price()
