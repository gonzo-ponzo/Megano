from django.views import View
from order.services import Cart, OrderFormation
from django.shortcuts import render, redirect, reverse, get_object_or_404
from product.models import Product
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from .forms import OrderForm
from copy import deepcopy


# Create your views here.
def cart_add(request, product_id: str, shop_id: str):
    if request.method == "GET":
        cart = Cart(request)
        product = get_object_or_404(Product, id=int(product_id))
        if cart.check_limits(product_id, shop_id):
            cart.add(product_id, str(shop_id))
            messages.success(request, f"{product.name} добавлен в корзину.")
        else:
            messages.error(request, f"{product.name} превышен остаток.")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def cart_lower(request, product_id: str, shop_id: str):
    if request.method == "GET":
        cart = Cart(request)
        product = get_object_or_404(Product, id=int(product_id))
        cart.lower(product_id, shop_id)
        messages.success(request, f"{product.name} убран из корзины.")
        return redirect("/order/cart/")


def cart_remove(request, product_id: str, shop_id: int):
    if request.method == "GET":
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product_id, shop_id)
        messages.success(request, f"{product.name} удален из корзины.")
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


class CreateOrderView(View):
    """Оформление заказа"""

    def get(self, request, *args, **kwargs):
        cart = deepcopy(request.user.cart)
        if not cart:
            raise PermissionDenied()

        if request.user.is_authenticated:
            context = {"order_form": OrderForm(), "order": OrderFormation.get_data_from_cart(cart)}
            print(context.get("order"))
            return render(request, "order/order.html", context=context)

        login_url = f"{reverse('login-page')}?next={reverse('order:create-order')}"
        return redirect(login_url)

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        context = {"order_form": order_form}
        if order_form.is_valid():
            print(order_form.cleaned_data)
            messages.success(request, "Хорошо")
            return render(request, "order/order.html", context=context)

        messages.error(request, "Ошибка")
        return render(request, "order/order.html", context=context)
