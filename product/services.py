from django.core.cache import cache
from django.conf import settings
from .models import ProductProperty, Property, Review


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


# class ComparisonList:
#     """
#     Список сравниваемых товаров
#     """
#
#     def get_list(self):
#         """Получить список сравниваемых товаров"""
#         compare_list = cache.get(settings.CACHE_KEY_COMPARISON)
#         attributes = dict()
#         if compare_list:
#
#             for product in compare_list:
#
#                 attributes_product = ProductProperty.objects.filter(product=product).values('property', 'value')
#
#                 for i_attribute in attributes_product:
#
#                     attribute = Property.objects.get(id=i_attribute['property'])
#                     value = i_attribute['value']
#                     if attribute not in attributes:
#                         attributes[attribute] = dict()
#                     attributes[attribute][product.id] = value
#
#         return attributes, compare_list
#
#     def add_item(self, product):
#         """Добавить товар в список сравнения"""
#         compare_list = cache.get(settings.CACHE_KEY_COMPARISON)
#         if not compare_list:
#             compare_list = set()
#         compare_list.add(product)
#         cache.set(settings.CACHE_KEY_COMPARISON, compare_list, settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_COMPARISON))
#
#     def remove_item(self, product):
#         """Удалить товар из списка сравнения"""
#         compare_list = cache.get(settings.CACHE_KEY_COMPARISON)
#         if product in compare_list:
#             compare_list.discard(product)
#             cache.set(settings.CACHE_KEY_COMPARISON, compare_list,
#                       settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_COMPARISON))
#
#     def clear_list(self):
#         """Удалить весь список сравнениваемых товаров"""
#         cache.delete(settings.CACHE_KEY_COMPARISON)


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
