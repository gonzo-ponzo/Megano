import random


CONST_STATUS_CHOICES = ((0, "Новый заказ"), (1, "Успешно оплачено"),
                        (2, "Оплата не выполнена, на вашем счёте не хватает средств"),
                        (3, "Оплата не выполнена, произошел сбой при списании средств"),
                        (4, "Духи коммуникаций сегодня не в настроении и ничего не переводят"),
                        (5, "Связь с Черным Вигвамом временно недоступна, ждите открытия нового портала"),
                        (6, "Служба Технической Поддержки Реальности извещает " +
                            "о временных сбоях в механизмах оплаты ништяков"),
                        (7, "Платеж не прошел по причине приглушенной громкости волн в эфире " +
                            "во имя избежания несвоевременного пробуждения Ктухлу"),
                        (8, "А волшебное слово? Без волшебного слова перевод не пройдет!"),
                        (9, "Товары эти не нужны тебе, на полках магазина оставь их"),
                        (10, "Что-то пошло не так. Попробуйте в другой раз"),)


class Pay:
    """
    Оплата заказа
    """

    @staticmethod
    def pay(payment):
        if payment.status != 0:
            return False
        res, info = Pay.validate_number(payment.card_number)
        payment.status = info[0]
        payment.save()
        return res

    @staticmethod
    def generate_random_score():
        """ (избыточный) аналог $('.Payment-generate') из scripts.js """
        bill_number = random.randint(10000000, 99999999)
        bill_number = str(bill_number)
        bill_number = f'{bill_number[:4]} {bill_number[4:]}'
        return bill_number

    @staticmethod
    def validate_number(bill_number):
        """ успешно, если номер четный, не больше 8ми символов и не заканчивается на ноль """
        error_messages = CONST_STATUS_CHOICES[2:]
        bill_number = "".join(bill_number.split())
        if len(bill_number) > 8 or len(set(bill_number) - set("0123456789")) > 0:
            return False, random.choice(error_messages)
        if bill_number[-1] in "2468":
            return True, CONST_STATUS_CHOICES[1]
        return False, random.choice(error_messages)
