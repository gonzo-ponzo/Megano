from django.views.generic import ListView, DetailView
from .models import PromotionOffer


# Create your views here.
class PromotionListView(ListView):
    model = PromotionOffer
    template_name = "promotion/promotions.html"
    paginate_by = 12 # 12 акций на страницы для комфортного просмотра


class PromotionView(DetailView):
    model = PromotionOffer
    template_name = "promotion/promotion.html"
