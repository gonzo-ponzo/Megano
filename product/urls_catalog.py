from django.urls import path
from .views import CatalogView


urlpatterns = [
    path("", CatalogView.as_view(), name="catalog-page"),
    path("<slug:category>/", CatalogView.as_view(), name="category-catalog-page"),
]
