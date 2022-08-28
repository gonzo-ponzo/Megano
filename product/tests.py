from django.test import TestCase
from django.urls import reverse

from product.models import Product


class ProductView(TestCase):
    def test_create_product(self):
        path = reverse("product-create")
        data = {"name": "Тестовый продукт"}
        response = self.client.post(path=path, data=data, content_type="application/json")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Product.objects.count(), 1)
