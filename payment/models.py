from django.db import models
from django.utils.translation import gettext_lazy as _

from .services import CONST_STATUS_CHOICES


class Payment(models.Model):
    STATUS_CHOICES = CONST_STATUS_CHOICES
    ''' в статусах: 0 - новый платеж в очереди,
                    1 - успешно оплаченный,
                    2 и больше - варианты неуспешных попыток оплаты'''

    order_number = models.IntegerField(verbose_name=_("номер заказа"))
    card_number = models.CharField(max_length=10, verbose_name=_("номер карты"))
    sum_to_pay = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("сумма к оплате"))
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name=_("статус платежа"))

    @property
    def get_status_text(self):
        return self.STATUS_CHOICES[self.status][1]

    class Meta:
        verbose_name = _("платеж")
        verbose_name_plural = _("платежи")
