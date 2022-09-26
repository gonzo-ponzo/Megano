from order.services import Cart
from django.shortcuts import render, redirect, get_object_or_404
from product.models import Product
from django.contrib import messages
from django.http import HttpResponseRedirect


# Create your views here.
def cart_add(request, pk: int, shop_id: int):
    if request.method == "GET":
        if request.user.is_authenticated:
            cart = Cart(request=request, user_cart=request.user.cart)
        else:
            cart = Cart(request)
        product = get_object_or_404(Product, id=pk)
        if cart.check_limits(pk, shop_id):
            cart.add(request, product=product, shop_id=shop_id)
            messages.success(request, f'{product.name} добавлен в корзину.')
        else:
            messages.error(request, f'{product.name} превышен остаток.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart_lower(request, pk, shop_id: int):
    if request.method == "GET":
        if request.user.is_authenticated:
            cart = Cart(request=request, user_cart=request.user.cart)
        else:
            cart = Cart(request)
        product = get_object_or_404(Product, id=pk)
        cart.lower(request, product=product, shop_id=shop_id)
        messages.success(request, f'{product.name} убран из корзины.')
        return redirect("/order/cart/")


def cart_remove(request, pk, shop_id: int):
    if request.method == "GET":
        if request.user.is_authenticated:
            cart = Cart(request=request, user_cart=request.user.cart)
        else:
            cart = Cart(request)
        product = get_object_or_404(Product, id=pk)
        cart.remove(request, product, shop_id=shop_id)
        messages.success(request, f'{product.name} удален из корзины.')
        return redirect("/order/cart/")


def cart_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            cart = Cart(request=request, user_cart=request.user.cart)
        else:
            cart = Cart(request)

        return render(
            request, "order/cart.html", {"cart": cart, "cart_counter": len(cart), "cart_price": cart.get_total_price()}
        )
