from django.urls import reverse
from timestamps.models import models, Model
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from product.models import Offer
from payment.services import CONST_STATUS_CHOICES
from django.db import transaction

User = get_user_model()


class Order(Model):
    """Заказ"""

    DELIVERY_CHOICES = ((1, _("Обычная доставка")), (2, _("Экспресс-доставка")))
    PAYMENT_CHOICES = ((1, _("Онлайн картой")), (2, _("Онлайн со случайного чужого счёта")))
    STATUS_CHOICES = ((1, "Новый заказ"), (2, "Ожидается оплата"), (3, _("Оплачен")), (4, _("Не оплачен")))
    ERROR_CHOICES = ((1, "Сервер оплаты не доступен"),) + CONST_STATUS_CHOICES[2:]

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("пользователь"))
    city = models.CharField(max_length=100, verbose_name=_("город"))
    address = models.CharField(max_length=512, verbose_name=_("адрес"))
    comment = models.TextField(blank=True, verbose_name=_("комментарий"))
    delivery_type = models.IntegerField(
        choices=DELIVERY_CHOICES, verbose_name=_("тип доставки"), default=DELIVERY_CHOICES[0][0]
    )
    payment_type = models.IntegerField(
        choices=PAYMENT_CHOICES, verbose_name=_("способ оплаты"), default=PAYMENT_CHOICES[0][0]
    )
    status_type = models.IntegerField(
        choices=STATUS_CHOICES, verbose_name=_("статус заказа"), default=STATUS_CHOICES[0][0]
    )
    error_type = models.IntegerField(blank=True, null=True, choices=ERROR_CHOICES, verbose_name=_("ошибка заказа"))
    delivery = models.ForeignKey("Delivery", on_delete=models.DO_NOTHING, verbose_name=_("доставка"))
    offer = models.ManyToManyField(Offer, through="OrderOffer", verbose_name=_("заказанные продукты"))

    def get_absolute_url(self):
        return reverse("order:history-order-detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("заказ")
        verbose_name_plural = _("заказы")


class OrderOffer(Model):
    """Товар в заказе"""

    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, verbose_name=_("заказ"))
    offer = models.ForeignKey(Offer, on_delete=models.DO_NOTHING, verbose_name=_("предложение магазина"))
    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("цена"))
    discount = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2, verbose_name=_("скидка"))
    amount = models.PositiveIntegerField(default=1, verbose_name=_("количество"))

    class Meta:
        verbose_name = _("товар в заказе")
        verbose_name_plural = _("товары в заказе")


class Delivery(Model):
    """Цена доставки"""

    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("цена"))
    express_price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("экспресс-цена"))
    sum_order = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("мин. цена корзины"))

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.deleted_at is None:
                Delivery.objects.delete()
                self.id = None
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("цена доставки")
        verbose_name_plural = _("цены доставки")
