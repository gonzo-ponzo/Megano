from random import randint
from functools import reduce
from urllib.parse import urlencode
from copy import copy
from statistics import mean

from django.db.models.query import QuerySet
from django.db.models import F, Q, Min, Max, Sum, Count, Avg, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.conf import settings

from .models import Product, ProductImage, Offer, ProductProperty, Property, Review, ProductCategory, ProductView
from order.models import OrderOffer
from shop.models import Shop
from user.models import CustomUser


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
        return list(range(Review.MIN_GRADE, Review.MAX_GRADE + 1))


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
        if self.category == "None":
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
                    a = "-"
                i.set_product(a)

        if self.short_list:
            for k, i in copy(self.attribute_list).items():
                if len(set(i.product_list)) == 1:
                    self.attribute_list.pop(k)

        self.get_product_list()

    def get_product_list(self):
        """
        Получение списка продуктов в сравнении
        """
        return [
            i for i in self.product_list.values() if self.category == "None" or self.category == str(i.category.id)
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
        self.rating = self.get_rating_list(product)

        self.min_price = "нет предложений"
        if product.deleted_at is None:
            min_price = product.offer_set.filter(
                amount__gt=0,
                deleted_at=None
            ).values_list("price", flat=True)
            if min_price:
                self.min_price = f"{min(min_price)} руб."

    def get_rating_list(self, product):
        """
        Определяем средний рейтинг продукта в сравнении
        """
        rating_list = product.review_set.all().values_list("rating", flat=True)
        if rating_list:
            avg_rating = mean(rating_list)
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


class QuerysetForCatalog:

    @staticmethod
    def get_queryset_for_catalog(without_offer=True):
        queryset = Product.objects.all()
        if without_offer:
            queryset = queryset.filter(offer__isnull=False)
        queryset = queryset.prefetch_related("productimage_set")
        queryset = queryset.select_related("category").defer('category__created_at',
                                                             'category__updated_at',
                                                             'category__deleted_at',
                                                             'category__description',
                                                             'category__slug',
                                                             'category__parent_id',
                                                             'category__lft',
                                                             'category__rght',
                                                             'category__tree_id')
        # queryset = queryset.prefetch_related('shop')
        queryset = queryset.annotate(offer_count=Count("offer", distinct=True))
        queryset = queryset.annotate(min_price=Min("offer__price"))
        queryset = queryset.annotate(review_count=Count("review", distinct=True))
        queryset = queryset.annotate(rating=Avg("review__rating", default=0))

        offers = Offer.objects.filter(product=OuterRef('pk')).values('product')
        rest_product = offers.annotate(total=Sum('amount')).values('total')
        queryset = queryset.annotate(rest=Subquery(rest_product))

        paid_orders = OrderOffer.objects\
            .filter(order__status_type=3, offer__product=OuterRef('pk'))\
            .values('offer__product')
        sold_product = paid_orders.annotate(total=Sum('amount')).values('total')
        queryset = queryset.annotate(sold=Coalesce(Subquery(sold_product), 0))

        queryset = queryset.order_by("pk")
        return queryset


class FilterProductsResult(QuerysetForCatalog):
    """
    Фильтр для списка продуктов
    """

    filter_field_name = (
        "fil_title",
        "fil_actual",
        "fil_limit",
        "fil_shop",
        "fil_price",
    )

    def __init__(self, **get_params):
        """
        :param get_params: параметры строки запроса
        """

        self.__queryset = self.get_queryset_for_catalog()
        self.title = get_params.get("fil_title", None)
        self.actual = bool(get_params.get("fil_actual"))
        self.limit = bool(get_params.get("fil_limit"))
        self.shop = get_params.get("fil_shop", None)
        price = get_params.get("fil_price", "").split(";")
        self.min_price = self.max_price = None
        if len(price) == 2 and price[0].isdigit() and price[1].isdigit():
            self.min_price, self.max_price = map(int, price)

    @property
    def queryset(self):
        return self.__queryset

    @classmethod
    def make_filter_part_url(cls, get_params: dict):
        filter_params = {key: get_params.get(key) for key in cls.filter_field_name if key in get_params}
        return urlencode(filter_params)

    def price_range(self) -> dict:
        """
        :return: словарь с максимальной и минимальной стоимостью текущего набора продуктов
        """
        return self.__queryset.aggregate(min=Min("min_price"), max=Max("min_price"))

    def all_filter_without_price(self) -> None:
        """Отфильтровать self.products по всем параметрам, кроме цены"""
        self.by_keywords()
        self.by_shop()
        if self.actual:
            self.only_actual()
        if self.limit:
            self.only_limited()

    def by_category(self, category: ProductCategory):
        self.__queryset = self.__queryset.filter(category__in=category.get_descendants(include_self=True))

    def by_keywords(self):
        if self.title:
            self.__queryset = self.__queryset.filter(name__icontains=self.title)

    def with_promo(self):
        self.__queryset = self.__queryset.filter(offer__promotionoffer__is_active=True)

    def only_actual(self):
        self.__queryset = self.__queryset.filter(rest__gt=0)

    def only_limited(self):
        self.__queryset = self.__queryset.filter(limited=True)

    def by_shop(self):
        """Фильтрация по продавцу"""
        if self.shop:
            self.__queryset = self.__queryset.filter(shop__name=self.shop)

    def by_price(self):
        """Фильтрация по цене"""
        if self.min_price and self.max_price:
            self.__queryset = self.__queryset.filter(min_price__gte=self.min_price, min_price__lte=self.max_price)


class SortProductsResult:
    """
    Сортировка результатов поиска продуктов
    """

    # поля, по которым проводится сортировка, кортеж кортежей вида
    # (значение параметра sort_by в строке запроса, наименование поля на сайте)
    fields = (
        ("price", _("цене")),
        ("popular", _("популярности")),
        ("rating", _("рейтингу")),
        ("new", _("новизне")),
    )
    css_class_for_increment = "Sort-sortBy_inc"
    css_class_for_decrement = "Sort-sortBy_dec"

    def __init__(self, products: QuerySet):
        """
        :param products: Queryset c необходимыми полями
        """
        self.products = products

    @classmethod
    def make_sort_part_url(cls, get_params: dict):
        sort_params = {
            "sort_by": get_params.get("sort_by", None),
            "reverse": get_params.get("reverse", ""),
        }
        return urlencode(sort_params)

    def sort_by_params(self, **get_params) -> QuerySet:
        sort_by = get_params.get("sort_by", None)
        sort_revers = bool(get_params.get("reverse"))

        if sort_by == "price":
            return self.by_price(reverse=sort_revers)
        if sort_by == "new":
            return self.by_newness(reverse=sort_revers)
        if sort_by == "rating":
            return self.by_review(reverse=sort_revers)
        if sort_by == "popular":
            return self.by_popularity(reverse=sort_revers)

        return self.products

    @classmethod
    def get_data_for_sort_links(cls, **get_params) -> list[dict]:
        sort_by = get_params.get("sort_by", None)
        sort_revers = bool(get_params.get("reverse", False))
        result = []
        for field in cls.fields:
            css_class = reverse = ""

            if field[0] == sort_by:
                if sort_revers:
                    css_class = cls.css_class_for_decrement
                else:
                    css_class = cls.css_class_for_increment
                    reverse = "&reverse=True"

            result.append(
                {
                    "css_class": css_class,
                    "title": field[1],
                    "arg_str": f"sort_by={field[0]}{reverse}",
                }
            )
        return result

    def by_popularity(self, reverse=False) -> QuerySet:
        field = "sold"
        if not reverse:
            field = "-" + field
        return self.products.order_by(field)

    def by_price(self, reverse=False) -> QuerySet:
        field = "min_price"
        if field not in self.products.query.annotations:
            self.products = self.products.annotate(min_price=Min("offer__price"))
        if reverse:
            return self.products.order_by(F(field).asc(nulls_last=True))
        else:
            return self.products.order_by(F(field).desc(nulls_last=True))

    def by_review(self, reverse=False) -> QuerySet:
        field = "rating"
        if not reverse:
            field = "-" + field
        return self.products.order_by(field)

    def by_newness(self, reverse=False) -> QuerySet:
        field = "created_at"
        if reverse:
            field = "-" + field
        return self.products.order_by(field)


class DailyOffer:

    __instance = None
    __not_use = True

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        if self.__class__.__not_use:
            # Задаем атрибуты для инициализации первого и единственного экземпляра
            self.__product = None
            self.__day = None
            self.__date_expired = None
            self.change_product()

    @staticmethod
    def __get_random_product():
        queryset = QuerysetForCatalog.get_queryset_for_catalog()
        queryset = queryset.only("id", "name", "category__name")
        queryset_for_choice = queryset.filter(limited=True).filter(rest__gt=0)
        if not queryset_for_choice:
            queryset_for_choice = queryset
        count = queryset_for_choice.count()
        if count == 0:
            return
        n = 0 if count == 1 else randint(0, count - 1)
        return queryset_for_choice[n]

    def change_product(self):
        self.__product: Product = self.__get_random_product()
        self.__date_expired = self.get_date_expired()
        if self.__product:
            self.__class__.__not_use = False
            self.__product.expired = (self.__date_expired + timezone.timedelta(days=1)).strftime("%d.%m.%Y %H:%M")
        else:
            self.__class__.__not_use = True

    @staticmethod
    def get_date_expired():
        current_local_time = timezone.localtime(timezone=timezone.get_fixed_timezone(180))
        tomorrow = current_local_time + timezone.timedelta(days=1)
        date_exp = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        # example of how to change expired date
        # date_exp = (current_local_time + timezone.timedelta(minutes=1)).replace(second=0, microsecond=0)
        return date_exp

    @property
    def product(self) -> Product:
        if self.__date_expired < timezone.now():
            self.change_product()
        return self.__product

    @property
    def product_id(self):
        if self.__product:
            return self.__product.id


class SearchProduct(QuerysetForCatalog):
    """
    Поиск продукта
    """

    def __init__(self, search_query=None):
        self.__search_query = self.__handle_search_string(search_query)
        if self.__search_query:
            self.__queryset = self.get_queryset_for_catalog(without_offer=False)
            self.search()
        else:
            self.__queryset = Product.objects.none()

    @staticmethod
    def __handle_search_string(search_query):
        """Разбиваем запрос на слова, оставляем слова длиной 3 и больше символа """
        if search_query:
            search_query = [word for word in search_query.split() if len(word) >= 3]
        return search_query

    def search(self):

        in_name = []
        in_description = []

        for word in self.__search_query:
            in_name.append(Q(name__icontains=word))
            in_description.append(Q(description__icontains=word))

        in_name = reduce(lambda a, b: a & b, in_name)
        in_description = reduce(lambda a, b: a & b, in_description)

        self.__queryset = self.__queryset.filter(in_name | in_description)

    @property
    def queryset(self):
        return self.__queryset


class BrowsingHistory:
    """
    История просмотра пользователя
    """

    def __init__(self, user: CustomUser):
        self.user = user

    def add_product_to_history(self, product: Product):
        """Добавить продукт в список просмотренных или обновить дату просмотра, если он там уже есть"""
        if not self.user.is_authenticated:
            return

        ProductView.objects.update_or_create(
            user=self.user,
            product=product,
        )

    def __len__(self):
        return self.count

    @property
    def count(self):
        """Количество просмотренных продуктов"""
        return ProductView.objects.filter(user=self.user).count()

    def delete_product_from_history(self, product: Product):
        """Удалить продукт из истории просмотров"""
        ProductView.objects.filter(
            user=self.user,
            product=product,
        ).delete()

    def clear_history(self):
        """Очистить историю просмотров"""
        ProductView.objects.filter(
            user=self.user,
        ).delete()

    def get_history(self, number_of_entries=20):
        """Получить последние записи истории просмотренных товаров"""
        products = QuerysetForCatalog.get_queryset_for_catalog(without_offer=False)
        products = products.filter(id__in=ProductView.objects.filter(user=self.user).values_list("product"))
        products = products.annotate(date_view=F("productview__updated_at"))
        products = products.order_by("-date_view")
        return products[:number_of_entries]


class ImportProducts:
    """
    Импорт данных о продуктах из файла
    """

    def import_from_dir(self):
        pass


class DetailedProduct:
    def __init__(self, product: Product):
        self.product = product

    def get_main_pic(self):
        """
        Получение активного изображения продукта
        """
        try:
            main_pic = ProductImage.objects.filter(product=self.product)[0].image
        except Exception:
            main_pic = None
        return main_pic

    def get_secondary_pics(self):
        """
        Получение всех изображений продукта за исключением активного
        """
        try:
            pics = ProductImage.objects.all().filter(product_id=self.product.id)[1:]
        except ProductImage.DoesNotExist:
            pics = None
        return pics

    def get_prices(self):
        """
        Получение всех цен на продукт
        """
        try:
            prices = Offer.objects.all().filter(product_id=self.product.id)
        except Offer.DoesNotExist:
            prices = None
        return prices

    def get_min_price(self):
        """
        Получение минимальной цены продукта
        """
        try:
            min_price = min([offer.price for offer in self.get_prices()])
        except Exception:
            return None
        return min_price

    def get_top_price(self):
        """
        Получение максимальной цены продукта
        """
        try:
            max_price = max([offer.price for offer in self.get_prices()])
        except Exception:
            if len(self.get_prices()) == 1:
                return self.get_prices()[0].price
            else:
                return None
        return max_price

    def get_discount(self):
        """
        Получение скидки на продукт в процентах
        """
        try:
            if self.get_top_price() == self.get_min_price():
                return None
            discount = int(((self.get_top_price() - self.get_min_price()) / self.get_top_price()) * 100)
        except Exception:
            return None
        return discount

    def get_description(self):
        """
        Получение описания продукта
        """
        try:
            description = get_object_or_404(Product, id=self.product.id).description
        except Product.DoesNotExist:
            description = None
        return description

    def get_property_values(self):
        """
        Получение значений свойств продукта
        """
        try:
            property_values = ProductProperty.objects.all().filter(product_id=self.product)
        except Property.DoesNotExist:
            property_values = None
        return property_values

    def get_property_idx(self):
        """
        Получение значений id свойств продукта
        """
        property_idx = [value.property_id for value in self.get_property_values()]
        return property_idx

    def get_property_names(self):
        """
        Получение наименований свойств продукта
        """
        try:
            property_names = [Property.objects.get(id=idx).name for idx in self.get_property_idx()]
        except Property.DoesNotExist:
            property_names = None
        return property_names

    def get_property_dict(self):
        """
        Получение словаря свойств-значений продукта
        """
        property_dict = zip(self.get_property_names(), self.get_property_values())
        return property_dict

    def get_offer_list(self):
        """
        Получение словаря магазин-цена продукта
        """
        try:
            offers = Offer.objects.all().filter(product_id=self.product)
        except Offer.DoesNotExist:
            offers = None
        offer_list = [(get_object_or_404(Shop, id=offer.shop_id), offer.price, offer.amount) for offer in offers]
        return offer_list

    def get_review(self):
        """
        Получение всех отзывов о продукте
        """
        try:
            reviews_list = Review.objects.all().filter(product_id=self.product.id)
            reviews = [(review, get_object_or_404(CustomUser, id=review.user_id)) for review in reviews_list]
        except Review.DoesNotExist:
            reviews = None
        return reviews


class PopularCategory:

    __count = 3

    @classmethod
    def get_cached(cls):

        category = cache.get_or_set(
            key=settings.CACHE_KEY_POPULAR_CATEGORY,
            default=cls.get_popular_category,
            timeout=settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_POPULAR_CATEGORY, 60 * 60 * 24)
        )
        return category

    @classmethod
    def get_popular_category(cls):
        category = cls.__get_needed_category()
        category = cls.__annotate_parameter_and_sort(category)
        category = category[:cls.__count]
        category = cls.__add_foto_and_price(category)

        return list(category)

    @staticmethod
    def __get_needed_category():
        category = ProductCategory.objects.all()
        return category

    @staticmethod
    def __annotate_parameter_and_sort(category):
        """Аннотация полем parameter - количество просмотров товаров в категориях и сортировка по нему"""
        category = ProductCategory.objects.add_related_count(
            queryset=category,
            rel_model=ProductView,
            rel_field="product__category",
            count_attr="parameter",
            cumulative=False,
        )
        category = category.order_by("-parameter")
        return category

    @staticmethod
    def __add_foto_and_price(category):
        category = category.annotate(min_price=Min("product__offer__price"))
        fotos = ProductImage.objects.filter(product__category_id=OuterRef("id")).order_by("?")
        category = category.annotate(foto=Subquery(fotos.values("image")[:1]))

        return category
