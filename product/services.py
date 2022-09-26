from copy import copy
from statistics import mean
from django.core.exceptions import ObjectDoesNotExist
from .models import Review, Product, ProductProperty


class ReviewForItem:
    """Отзывы к товарам"""

    def __init__(self, product):
        self._product = product

    def add_review(self, rating: int, text: str, user):
        """Добавить отзыв"""
        review = self.get_review(product=self._product, user=user, rating=rating, text=text)
        if not review:
            Review.objects.create(rating=rating, text=text, product=self._product, user=user)

    @classmethod
    def delete_review(cls, pk: int):
        """Удалить отзыв"""
        review = cls.get_review(pk=pk)
        if review:
            review.delete()

    @classmethod
    def get_review(cls, **kwargs):
        """Получить отзыв"""
        return Review.objects.filter(**kwargs)

    def get_reviews_product(self):
        """Получить отзывы продукта"""

        return (
            Review.objects.filter(product=self._product)
            .select_related("user")
            .only("pk", "created_at", "text", "rating", "user__avatar", "user__first_name")
            .order_by("-created_at")
        )

    def get_count_reviews_product(self):
        """Получить кол-во отзывов"""
        return self.get_reviews_product().count()

    @staticmethod
    def get_stars_order_by():
        """Список оценок"""
        return [star for star in range(Review.MIN_GRADE, Review.MAX_GRADE + 1)]


class ProductCompareList:
    """
    Объект подготовки данных для сравнения продуктов
    """

    def __init__(self, product_list_id, short_list, category):
        attributes = ProductProperty.objects.filter(product__in=product_list_id)
        self.attribute_list = dict()
        self.short_list = short_list
        self.category = category
        products = Product.objects.filter(id__in=product_list_id)
        self.category_list = set(i.category for i in products)
        if self.category == 'None':
            products_list = products
        else:
            products_list = products.filter(category=self.category)

        self.product_list = {i.id: ProductCompare(i) for i in products_list}

        for i in set(i.property for i in attributes):
            self.attribute_list[i.id] = PropertyCompare(i)

        for k, i in self.attribute_list.items():
            for m, j in self.product_list.items():
                try:
                    a = attributes.get(product=m, property=k).value
                except ObjectDoesNotExist:
                    a = '-'
                i.set_product(a)

        if self.short_list:
            for k, i in copy(self.attribute_list).items():
                if len(set(i.product_list)) == 1:
                    self.attribute_list.pop(k)

        self.get_product_list()

    def get_product_list(self):
        return [
            i for i in self.product_list.values()
            if self.category == 'None' or self.category == str(i.category.id)
        ]


class ProductCompare:
    """
    Обработка данных для сравнения по продукту
    """

    def __init__(self, product):
        self.id = product.id
        self.name = product.name
        self.category = product.category
        self.manufacturer = product.manufacturer
        self.image = product.productimage_set.first()
        self.min_price = min(product.offer_set.all().values_list('price', flat=True))
        self.rating = self.get_rating_list(product)

    def get_rating_list(self, product):
        rating_list = product.review_set.all().values_list('rating', flat=True)
        if rating_list:
            avg_rating = mean(product.review_set.all().values_list('rating', flat=True))
            star_list = list()
            for i in range(5):
                if avg_rating > 1:
                    star_list.append(100)
                    avg_rating -= 1
                elif avg_rating == 0:
                    star_list.append(0)
                else:
                    star_list.append(int(avg_rating * 100))
                    avg_rating = 0
            return star_list


class PropertyCompare:
    """
    Подготовка списков атрибутов продуктов для вывода при сравнении
    """

    def __init__(self, attribute):
        self.name = attribute.name
        self.product_list = list()
        self.use_in_short_list = True

    def set_product(self, attribute):
        self.product_list.append(attribute)

    def get_attribute_list(self):
        return self.product_list


class ProductsFilter:
    """
    Фильтр для списка продуктов
    """

    def filter(self):
        """Отфильтровать список по указанным параметрам"""
        self.by_price()
        self.by_keywords()
        self.by_seller()
        return

    def by_price(self):
        """Фильтрация по цене"""
        pass

    def by_keywords(self):
        """Фильтрация по ключевым словам в названии"""
        pass

    def by_seller(self):
        """Фильтрация по продавцу"""
        pass


class SortProductsResult:
    """
    Сортировка результатов поиска продуктов
    """

    def by_popularity(self):
        """По популярности"""
        pass

    def by_price(self):
        """По цене"""
        pass

    def by_review(self):
        """По отзывам"""
        pass

    def by_newness(self):
        """По новизне"""
        pass


class SearchProduct:
    """
    Поиск продукта
    """

    def search(self):
        pass


class BrowsingHistory:
    """
    История просмотра пользователя
    """

    def add_product_to_history(self):
        """Добавить продукт в список просмотренных"""
        pass

    def get_history(self):
        """Получить список просмотренных товаров"""
        pass


class ImportProducts:
    """
    Импорт данных о продуктах из файла
    """

    def import_from_dir(self):
        pass
