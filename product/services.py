from product.models import Product, Offer


class ReviewForItem:
    """
    Отзывы к товарам
    """

    def add_review(self):
        """Добавить отзыв"""
        pass

    def edit_review(self):
        """Редактировать отзыв"""
        pass


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


class GetProduct:
    """
    Получить список товаров при выборе категории
    """
    def get_product_list(self, category_tree: list[str]):
        queryset = Product.objects.all()
        for item in queryset:
            average_price = self.get_average_price(product=item)
            item.average_price = average_price

            # Проверить наличие скидки на товар и применить ее. Пока просто вычитаю, изображая скидку
            item.price_with_discount = average_price - 1000

        return queryset

    def get_average_price(self, product) -> float:
        offers = Offer.objects.filter(product=product)
        return sum([item.price for item in offers]) / len(offers)

    def check_discount_and_apply(self, item):
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
