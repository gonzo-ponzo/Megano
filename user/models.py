from timestamps.models import models, Model
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Profile(Model):
    """Профиль"""
    user = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name=_("пользователь"))
    middle_name = models.CharField(max_length=150, blank=True, verbose_name=_("отчество"))
    phone = models.CharField(max_length=20, verbose_name=_("телефон"))
    avatar = models.ImageField(blank=True, upload_to='static/img/avatar', verbose_name=_("фото"))

    class Meta:
        verbose_name = _("профиль")
        verbose_name_plural = _("профили")
