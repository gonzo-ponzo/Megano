import random


class Pay:
    """
    Оплата заказа
    """

    def pay(self):
        pass

    def generate_random_score(self):
        """ аналог $('.Payment-generate') из scripts.js """
        bill_number = random.randint(10000000, 99999999)
        bill_number = str(bill_number)
        bill_number = f'{bill_number[:4]} {bill_number[4:]}'
        return bill_number

    def validate_number(self, bill_number):
        """ успешно, если номер четный, не больше 8ми символов и не заканчивается на ноль """
        error_messages = ["связь с Черным Вигвамом временно недоступна, ждите открытия нового портала", "Служба Технической Поддержки Реальности извещает о временных сбоях в механизмах оплаты ништяков", "платеж не прошел по причине приглушенной громкости волн в эфире во имя избежания несвоевременного пробуждения Ктухлу", "а волшебное слово? без волшебного слова перевод не пройдет!", "товары эти не нужны тебе, на полках магазина оставь их"]
        bill_number = "".join(bill_number.split())
        if len(bill_number) > 8 or len(set(bill_number) - set("0123456789")) > 0:
            return False, random.choice(error_messages)        
        if bill_number[-1] in "2468":
            return True, "оплачено"
        return False, random.choice(error_messages)
