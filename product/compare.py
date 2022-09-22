from product.models import Product, ProductProperty


class ProductCompare:

    def __init__(self, product_list):
        self.product_set = dict()
        for i in Product.objects.filter(id__in=product_list):
            self.product_set[i.id] = ProductProperties(i)

    def get_property_list(self):
        property_list = list()
        for i in self.product_set.values():
            property_list += i.get_property_list()
        return set(property_list)


class ProductProperties:

    def __init__(self, product):
        self.product = product
        self.name = product.name
        self.price = min(i.price for i in product.offer_set.all())
        self.pic = product.productimage_set.first().image
        self.attributes = {k.property: k for k in product.productproperty_set.all()}

    def get_property_list(self):
        return self.attributes.keys()




