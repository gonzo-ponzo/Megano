from django.views.generic import TemplateView
from .models import Promotion

# Create your views here.


class PromotionView(TemplateView):
    model = Promotion
    template_name = 'promotion/promotion.html'
    context_objects_name = 'promotion_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list'] = Promotion.objects.all()
        return context
