from django.db import models
from django.utils.translation import gettext_lazy as _


class Process(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_("процесс"))
    is_run = models.BooleanField(default=False, verbose_name=_("запущен"))

    class Meta:
        permissions = [
            ("start_import", _("Запускать импорт")),
        ]
