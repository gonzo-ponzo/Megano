from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import PromotionOffer
from django.core.cache import cache
from .services import DetailedPromotion

# Create your views here.


class PromotionListView(ListView):
    model = PromotionOffer
    template_name = "promotion/promotions.html"
    paginate_by = 12


class PromotionView(DetailView):
    model = PromotionOffer
    template_name = "promotion/promotion.html"
