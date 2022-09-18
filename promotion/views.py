from django.views.generic import TemplateView
from .models import PromotionOffer

# Create your views here.


class PromotionView(TemplateView):
    model = PromotionOffer
    template_name = "promotion/promotion.html"
    context_objects_name = "promotion_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list"] = PromotionOffer.objects.all()
        return context
