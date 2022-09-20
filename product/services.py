from .models import Product, ProductImage, Offer, ProductProperty, Property, Review
from shop.models import Shop
from user.models import CustomUser
from django.shortcuts import get_object_or_404


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


class DetailedProduct:
    def __init__(self, product: Product):
        self.product = product

    def get_main_pic(self):
        """
        Получение активного изображения продукта
        """
        try:
            main_pic = ProductImage.objects.all().filter(product_id=self.product.id)[0].image
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
            property_names = [get_object_or_404(Property, id=idx).name for idx in self.get_property_idx()]
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
