from product.models import Product, ProductProperty


class ProductCompare:

    def __init__(self, product_list):
        self.product_set = dict()
        for i in Product.objects.filter(id__in=product_list):
            self.product_set[i.id] = i

    def get_property_list(self):
        property_list = list()
        for i in self.product_set.values():
            property_list += i.get_property_list()
        return set(property_list)
