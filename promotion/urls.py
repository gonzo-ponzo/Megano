from django.urls import path
from .views import PromotionView

urlpatterns = [
    path("", PromotionView.as_view(), name="promotion-page"),
]
