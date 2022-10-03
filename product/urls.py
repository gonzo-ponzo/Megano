from django.urls import path
from .views import CreateProductView, CompareView, DetailedProductView, CompareAdd, CompareRemove, CompareClear


urlpatterns = [
    path("create/", CreateProductView.as_view(), name="product-create"),
    path("compare/", CompareView.as_view(), name="compare-page"),
    path("<int:pk>/", DetailedProductView.as_view(), name="product-page"),
    path('compare_add/<int:pk>', CompareAdd.as_view(), name='compare_add'),
    path('compare_remove/<int:pk>', CompareRemove.as_view(), name='compare_remove'),
    path('compare_clear/', CompareClear.as_view(), name='compare_clear'),
    path('<int:pk>/', DetailedProductView.as_view(), name='product-page')
]
