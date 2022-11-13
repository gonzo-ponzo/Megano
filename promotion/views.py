from django.views.generic import ListView, DetailView
from .models import PromotionOffer
from constance import config


# Create your views here.
class PromotionListView(ListView):
    model = PromotionOffer
    template_name = "promotion/promotions.html"

    def get_paginate_by(self, queryset):
        return config.OBJECTS_PER_PAGE


class PromotionView(DetailView):
    model = PromotionOffer
    template_name = "promotion/promotion.html"
