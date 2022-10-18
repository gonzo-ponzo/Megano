from django.views import View
from django.conf import settings
from order.services import Cart, Checkout, SerializersCache, CheckoutDB
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
        cart = Cart(request)
        cart.refresh()
        is_authenticated = request.user.is_authenticated
        cart = request.user.cart if is_authenticated else request.session.get(settings.CART_SESSION_ID)

        if not cart:
            raise PermissionDenied()

        if is_authenticated:
            context = {
                "order_form": OrderForm(),
                "order": Checkout.get_data_from_cart(deepcopy(cart), request.user.id),
            }
            return render(request, "order/order.html", context=context)

        login_url = f"{reverse('login-page')}?next={reverse('order:create-order')}"
        return redirect(login_url)

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        order = SerializersCache.get_data_from_cache(f"{settings.CACHE_KEY_CHECKOUT}{user_id}")

        if order is None:
            messages.error(request, "Ошибка, попробуйте повторить оформление заказа")
            return redirect(reverse("order:cart-page"))

        order_form = OrderForm(request.POST)
        msg = ""

        if order_form.is_valid():
            checkout_db = CheckoutDB(
                user_id=user_id, order_info=order_form.cleaned_data, order_data=order, cart=Cart(request)
            )
            status, msg = checkout_db.save_order()
            if status:
                messages.success(request, msg)
                # нужно переход на оплату сделать
                return redirect("main-page")

        msg = msg if msg else "Ошибка, проверьте заполнение данных"
        messages.error(request, msg)
        context = {"order_form": order_form, "order": order}
        return render(request, "order/order.html", context=context)
