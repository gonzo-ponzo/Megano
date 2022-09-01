from django.views import View
from django.views.generic import ListView, TemplateView, DetailView
from shop.models import Shop
from shop.services import ShopDetail
from django.shortcuts import render  # noqa: F401

# Create your views here.


class ShopListView(View):

    def get(self, request, *args, **kwargs):
        # shop_id = kwargs['pk']
        # shop = ShopDetail(0)
        # shop_description = shop.get_shop_description
        # print(2)
        # print(shop_description)
        render(request, 'shop/shop.html')


# class ContactsPage(TemplateView):
#     template_name = 'contacts.html'
