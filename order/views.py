from order.services import Cart
from django.shortcuts import render, redirect, get_object_or_404
from product.models import Product
from django.contrib import messages
from django.http import HttpResponseRedirect


# Create your views here.
def cart_add(request, product_id: str, shop_id: str):
    if request.method == "GET":
        cart = Cart(request)
        product = get_object_or_404(Product, id=int(product_id))
        if cart.check_limits(product_id, shop_id):
            cart.add(product_id, str(shop_id))
            messages.success(request, f'{product.name} добавлен в корзину.')
        else:
            messages.error(request, f'{product.name} превышен остаток.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart_lower(request, product_id: str, shop_id: str):
    if request.method == "GET":
        cart = Cart(request)
        product = get_object_or_404(Product, id=int(product_id))
        cart.lower(product_id, shop_id)
        messages.success(request, f'{product.name} убран из корзины.')
        return redirect("/order/cart/")


def cart_remove(request, product_id: str, shop_id: int):
    if request.method == "GET":
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product_id, shop_id)
        messages.success(request, f'{product.name} удален из корзины.')
        return redirect("/order/cart/")


def cart_clear(request):
    if request.method == "GET":
        cart = Cart(request)
        cart.clear()
        return redirect("/")


def cart_view(request):
    if request.method == "GET":
        cart = Cart(request)

        return render(
            request, "order/cart.html", {"cart": cart, "cart_counter": len(cart), "cart_price": cart.get_total_price()}
        )
