from django.urls import path
from .views import PromotionListView, PromotionView

urlpatterns = [
    path("", PromotionListView.as_view(), name="promotion-list-page"),
    path("<int:pk>/", PromotionView.as_view(), name="promotion-page"),
]
