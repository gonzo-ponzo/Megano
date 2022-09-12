from order.cart import Cart
from django.shortcuts import render, redirect, get_object_or_404
from product.models import Product


# Create your views here.
def cart_add(request, pk, shop_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=pk)
    cart.add(product=product, shop_id=shop_id)
    return redirect('/order/cart/')


def cart_lower(request, pk, shop_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=pk)
    cart.lower(product=product, shop_id=shop_id)
    return redirect('/order/cart/')


def cart_remove(request, pk, shop_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, id=pk)
    cart.remove(product, shop_id=shop_id)
    return redirect('/order/cart/')


def cart_view(request):
    cart = Cart(request)
    return render(request, 'order/cart.html', {
        'cart': cart,
        'cart_counter': len(cart),
        'cart_price': cart.get_total_price()
    })
