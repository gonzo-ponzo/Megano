
class ReviewForItem:
	"""
	Отзывы к товарам
	"""
	def add_review(self):
		pass

	def edit_review(self):
		pass


class ComparisonList:
	"""
	Список сравниваемых товаров
	"""
	def add_item(self):
		pass

	def remove_item(self):
		pass

	def get_compare_list(self):
		pass


class ViewedProducts:
	"""
	Список просмотренных товаров
	"""
	def add_viewed_product(self):
		pass

	def get_viewed_products_list(self):
		pass


class ProductsFilter:
	"""
	Фильтр для списка продуктов
	"""
	def filter(self):
		self.by_price()
		self.by_keywords()
		self.by_seller()
		return

	def by_price(self):
		pass

	def by_keywords(self):
		pass

	def by_seller(self):
		pass


class SortProductsResult:
	"""
	Сортировка результатов поиска продуктов
	"""

	def by_popularity(self):
		pass

	def by_price(self):
		pass

	def by_review(self):
		pass

	def by_newness(self):
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

	def rec_product_to_history(self):
		pass

	def get_history(self):
		pass

