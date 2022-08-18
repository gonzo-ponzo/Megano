
class UserCart:
	"""
	Корзина пользователя
	"""
	def add_product(self):
		"""Добавить продукт в корзину"""
		pass

	def remove_product(self):
		"""Удалить продукт из корзины"""
		pass

	def increase_count_of_product(self):
		"""Увеличить кол-во продукта в корзине"""
		pass

	def decrease_count_of_product(self):
		"""Уменьшить кол-во продукта в корзине"""
		pass

	def change_seller(self):
		"""Изменить продавца выбранного продукта"""
		pass

	def get_total_sum(self):
		"""Получить итоговую цену всех товаров в корзине"""
		pass


class Order:
	"""
	Составление заказа
	"""
	def set_user_param(self):
		pass

	def set_shipping_param(self):
		pass

	def set_pay_param(self):
		pass

	def get_order_status(self):
		pass


class Pay:
	"""
	Оплата заказа
	"""
	def pay(self):
		pass
