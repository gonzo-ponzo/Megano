from django import template
from order.cart import *

register = template.Library()


@register.simple_tag()
def get_cart_len(request):
    cart = Cart(request)
    return len(cart)


@register.simple_tag()
def get_cart_price(request):
    cart = Cart(request)
    return cart.get_total_price()
