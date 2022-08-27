from django.views.generic import ListView, TemplateView
from shop.models import Shop
from django.shortcuts import render

# Create your views here.
class ShopListView(ListView):
    model = Shop
    template_name = 'shop.html'
    context_objects_name = 'shop_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list'] = Shop.objects.all()
        return context


class ContactsPage(TemplateView):
    template_name = 'contacts.html'
