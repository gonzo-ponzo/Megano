from django import template
from order.services import Cart

register = template.Library()


@register.simple_tag()
def get_cart_len(request):
    if request.user.is_authenticated:
        cart = Cart(request=request, user_cart=request.user.cart)
    else:
        cart = Cart(request)
    return len(cart)


@register.simple_tag()
def get_cart_price(request):
    if request.user.is_authenticated:
        cart = Cart(request=request, user_cart=request.user.cart)
    else:
        cart = Cart(request)
    return cart.get_total_price()
