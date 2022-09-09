from django.test import TestCase
from django.urls import reverse

from product.models import Product, ProductCategory


class ProductView(TestCase):
    def test_create_product(self):
        path = reverse("product-create")
        data = {"name": "Тестовый продукт"}
        response = self.client.post(path=path, data=data, content_type="application/json")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Product.objects.count(), 1)


class ProductCategoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        parent_name = "parent"
        parent = ProductCategory.objects.create(name=parent_name, slug=parent_name)
        for i in range(3):
            child_name = f"child{i}"
            ProductCategory.objects.create(name=child_name, slug=child_name, parent=parent)

    def test_check_delete_parent_with_child(self):
        category = ProductCategory.objects
        category.get(name="child1").delete()
        self.assertEquals(category.count(), 3)
        category.filter(name="parent").delete()
        self.assertEquals(category.count(), 0)
