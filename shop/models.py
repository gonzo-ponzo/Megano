from timestamps.models import models, Model
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Shop(Model):
    """Магазин"""
    name = models.CharField(max_length=512, verbose_name=_("название"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    phone = models.CharField(max_length=20, verbose_name=_("телефон"))
    email = models.CharField(max_length=100, verbose_name=_("email"))
    address = models.CharField(max_length=512, verbose_name=_("адрес"))
    image = models.ImageField(blank=True, upload_to="shop/%Y/%m/%d", verbose_name=_("фото"))
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.PROTECT,
                                verbose_name=_("пользователь"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("магазин")
        verbose_name_plural = _("магазины")
