from django.core.cache import cache
from django.conf import settings


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

    def get_compare_list(self):
        """Получить список сравниваемых товаров"""
        compare_list = cache.get(settings.CACHE_KEY_COMPARISON)
        return compare_list

    def add_item(self, product):
        """Добавить товар в список сравнения"""
        compare_list = cache.get(settings.CACHE_KEY_COMPARISON)
        if not compare_list:
            compare_list = set()
        compare_list.add(product)
        cache.set(settings.CACHE_KEY_COMPARISON, compare_list, settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_COMPARISON))

    def remove_item(self, product):
        """Удалить товар из списка сравнения"""
        compare_list = cache.get(settings.CACHE_KEY_COMPARISON)
        if product in compare_list:
            compare_list.discard(product)
            cache.set(settings.CACHE_KEY_COMPARISON, compare_list,
                      settings.CACHE_TIMEOUT.get(settings.CACHE_KEY_COMPARISON))

    def clear_compare_list(self):
        """Удалить весь список сравнениваемых товаров"""
        cache.delete(settings.CACHE_KEY_COMPARISON)


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
