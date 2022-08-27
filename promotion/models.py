from django.db import models
from django.utils.translation import gettext_lazy as _


class Promotion(models.Model):
    """Акция"""
    name = models.CharField(max_length=512, verbose_name=_("название"))
