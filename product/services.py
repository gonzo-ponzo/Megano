from .models import Review
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _


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


class ComparisonList:
    """
    Список сравниваемых товаров
    """

    def add_item(self):
        """Добавить товар к сравнению"""
        pass

    def remove_item(self):
        """Удалить товар из списка сравнения"""
        pass

    def get_compare_list(self):
        """Получить список сравниваемых товаров"""
        pass


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
    fields = (
        ('price', _('цене')),
        ('popular', _('популярности')),
        ('reviews', _('отзывам')),
        ('new', _('новизне')),
    )
    css_class_for_increment = 'Sort-sortBy_inc'
    css_class_for_decrement = 'Sort-sortBy_dec'

    # default_sort_data = []
    # for field in fields:
    #     default_sort_data.append({
    #         'css_class': '',
    #         'title': field[1],
    #         'arg_str': f'sort_by={field[0]}',
    #     })

    def __init__(self, products: QuerySet, **sort_params):
        self.products = products
        self.sort_by = sort_params.get('sort_by', None)
        self.sort_revers = bool(sort_params.get('reverse', False))

    def get_data_for_sort_options(self):
        result = []
        for field in self.fields:
            css_class = reverse = ''

            if field == self.sort_by:
                if self.sort_revers:
                    css_class = self.css_class_for_decrement
                else:
                    reverse = '&reverse=True'

            result.append({
                'css_class': css_class,
                'title': field[1],
                'arg_str': f'sort_by={field[0]}{reverse}',
            })
        return result

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
