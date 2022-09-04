from timestamps.models import models, Model
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from product.models import Offer

User = get_user_model()


class Order(Model):
    """Заказ"""

    DELIVERIES = (_("Доставка"), _("Экспресс-доставка"))
    PAYMENTS = (_("Онлайн картой"), _("Онлайн со случайного чужого счёта"))

    # TODO над статусами и ошибками над еще подумать какие надо,
    #  и может вообще в отдельные таблицы занести
    STATUSES = (_("Оплачен"), _("Не оплачен"))
    ERRORS = (
        _("Оплата не выполнена, на вашем счёте не хватает средств"),
        _("Оплата не выполнена, произошел сбой при списании средств"),
    )

    DELIVERY_CHOICES = [(idx, value) for idx, value in enumerate(DELIVERIES)]
    PAYMENT_CHOICES = [(idx, value) for idx, value in enumerate(PAYMENTS)]
    STATUS_CHOICES = [(idx, value) for idx, value in enumerate(STATUSES)]
    ERROR_CHOICES = [(idx, value) for idx, value in enumerate(ERRORS)]

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("пользователь"))
    city = models.CharField(max_length=100, verbose_name=_("город"))
    address = models.CharField(max_length=512, verbose_name=_("адрес"))
    comment = models.TextField(blank=True, verbose_name=_("комментарий"))
    delivery_type = models.IntegerField(choices=DELIVERY_CHOICES, verbose_name=_("тип доставки"))
    payment_type = models.IntegerField(choices=PAYMENT_CHOICES, verbose_name=_("способ оплаты"))
    status_type = models.IntegerField(choices=STATUS_CHOICES, verbose_name=_("статус заказа"))
    error_type = models.IntegerField(blank=True, null=True, choices=ERROR_CHOICES, verbose_name=_("ошибка заказа"))
    delivery = models.ForeignKey(
        "Delivery", blank=True, null=True, on_delete=models.PROTECT, verbose_name=_("доставка")
    )
    offer = models.ManyToManyField(Offer, through="OrderOffer", verbose_name=_("заказанные продукты"))

    class Meta:
        verbose_name = _("заказ")
        verbose_name_plural = _("заказы")


class OrderOffer(Model):
    """Товар в заказе"""

    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name=_("заказ"))
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, verbose_name=_("предложение магазина"))
    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("цена"))
    amount = models.PositiveIntegerField(verbose_name=_("количество"))

    class Meta:
        verbose_name = _("товар в заказе")
        verbose_name_plural = _("товары в заказе")


class Delivery(Model):
    """Цена доставки"""

    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("цена"))
    express_price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("экспресс-цена"))
    sum_order = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("мин. цена корзины"))

    class Meta:
        verbose_name = _("цена доставки")
        verbose_name_plural = _("цены доставки")
