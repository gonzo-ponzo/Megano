from django.db.models.query import QuerySet
from django.db.models import F, Min, Avg, Max, Sum
from urllib.parse import urlencode
from django.utils.translation import gettext_lazy as _
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


class FilterProductsResult:
    """
    Фильтр для списка продуктов
    """
    filter_field_name = (
        'fil_title',
        'fil_actual',
        'fil_limit',
        'fil_shop',
        'fil_price',
    )

    def __init__(self, products: QuerySet, **get_params):
        """
        :param products: Queryset подготовленный функцией .utils.get_queryset_for_catalog
        """
        self.products = products
        self.title = get_params.get('fil_title', None)
        self.actual = bool(get_params.get('fil_actual'))
        self.limit = bool(get_params.get('fil_limit'))
        self.shop = get_params.get('fil_shop', None)
        price = get_params.get('fil_price', '').split(";")
        self.min_price = self.max_price = None
        if len(price) == 2 and price[0].isdigit() and price[1].isdigit():
            self.min_price, self.max_price = map(int, price)

    @classmethod
    def make_filter_part_url(cls, get_params: dict):
        filter_params = {key: get_params.get(key) for key in cls.filter_field_name if key in get_params}
        return urlencode(filter_params)

    def price_range(self) -> dict:
        """
        :return: словарь с максимальной и минимальной стоимостью из текущего набора продуктов
        """
        return self.products.aggregate(min=Min('min_price'), max=Max('min_price'))

    def all_filter_without_price(self) -> None:
        """Отфильтровать self.products по всем параметрам, кроме цены"""
        self.by_keywords()
        if self.actual: self.only_actual()
        if self.limit: self.only_limited()
        self.by_shop()

    def by_keywords(self):
        if self.title:
            self.products = self.products.filter(name__icontains=self.title)

    def only_actual(self):
        # self.products = self.products.filter(offer__isnull=False)
        self.products = self.products.annotate(rest=Sum('offer__amount'))
        self.products = self.products.filter(rest__gt=0)

    def only_limited(self):
        self.products = self.products.filter(limited=True)

    def by_shop(self):
        """Фильтрация по продавцу"""
        if self.shop:
            self.products = self.products.filter(shop__name=self.shop)

    def by_price(self):
        """Фильтрация по цене"""
        if self.min_price and self.max_price:
            self.products = self.products.filter(min_price__gte=self.min_price, min_price__lte=self.max_price)


class SortProductsResult:
    """
    Сортировка результатов поиска продуктов
    """
    # поля, по которым проводится сортировка, кортеж кортежей вида
    # (значение параметра sort_by в строке запроса, наименование поля на сайте)
    fields = (
        ('price', _('цене')),
        ('popular', _('популярности')),
        ('reviews', _('рейтингу')),
        ('new', _('новизне')),
    )
    css_class_for_increment = 'Sort-sortBy_inc'
    css_class_for_decrement = 'Sort-sortBy_dec'

    def __init__(self, products: QuerySet):
        """
        :param products: Queryset подготовленный функцией .utils.get_queryset_for_catalog
        """
        self.products = products

    @classmethod
    def make_sort_part_url(cls, get_params: dict):
        sort_params = {
            'sort_by': get_params.get('sort_by', None),
            'reverse': get_params.get('reverse', ''),
        }
        return urlencode(sort_params)

    def sort_by_params(self, **get_params) -> QuerySet:
        sort_by = get_params.get('sort_by', None)
        sort_revers = bool(get_params.get('reverse'))

        if sort_by == 'price':
            return self.by_price(reverse=sort_revers)
        if sort_by == 'new':
            return self.by_newness(reverse=sort_revers)
        if sort_by == 'reviews':
            return self.by_review(reverse=sort_revers)
        if sort_by == 'popular':
            return self.by_popularity(reverse=sort_revers)

        return self.products

    @classmethod
    def get_data_for_sort_links(cls, **get_params) -> list[dict]:
        sort_by = get_params.get('sort_by', None)
        sort_revers = bool(get_params.get('reverse', False))
        result = []
        for field in cls.fields:
            css_class = reverse = ''

            if field[0] == sort_by:
                if sort_revers:
                    css_class = cls.css_class_for_decrement
                else:
                    css_class = cls.css_class_for_increment
                    reverse = '&reverse=True'

            result.append({
                'css_class': css_class,
                'title': field[1],
                'arg_str': f'sort_by={field[0]}{reverse}',
            })
        return result

    def by_popularity(self, reverse=False) -> QuerySet:
        field = 'order_count'
        if not reverse:
            field = '-' + field
        return self.products.order_by(field)

    def by_price(self, reverse=False) -> QuerySet:
        field = 'min_price'
        if field not in self.products.query.annotations:
            self.products = self.products.annotate(min_price=Min('offer__price'))
        if reverse:
            return self.products.order_by(F(field).asc(nulls_last=True))
        else:
            return self.products.order_by(F(field).desc(nulls_last=True))

    def by_review(self, reverse=False) -> QuerySet:
        field = 'rating'
        if not reverse:
            field = '-' + field
        return self.products.order_by(field)

    def by_newness(self, reverse=False) -> QuerySet:
        field = 'created_at'
        if reverse:
            field = '-' + field
        return self.products.order_by(field)


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
