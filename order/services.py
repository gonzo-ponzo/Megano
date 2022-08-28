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

    def clear_cart(self):
        """Очистить корзину"""
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
        """Уточнить параметры пользователя"""
        pass

    def set_shipping_param(self):
        """Установить параметры доставки"""
        pass

    def set_pay_param(self):
        """Установить параметры доставки"""
        pass

    def get_order_status(self):
        """Получить статус заказа"""
        pass

    def set_order_status(self):
        """Изменить статус заказа"""
        pass


class OrderHistory:
    """История покупок"""

    def add_product_in_history(self):
        """Добавить продукт в историю покупок"""
        pass

    def get_history(self):
        """Получить историю покупок"""
        pass
