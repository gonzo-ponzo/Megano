from .models import Review, Product


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


class ProductCompare:

    def __init__(self, product_list):
        self.product_set = dict()
        for i in Product.objects.filter(id__in=product_list):
            self.product_set[i.id] = i

    def get_property_list(self):
        property_list = list()
        for i in self.product_set.values():
            property_list += i.get_attributes().keys()
        return set(property_list)


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
