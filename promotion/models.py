from timestamps.models import models, Model
from django.utils.translation import gettext_lazy as _

from product.models import Product


class Banner(Model):
    """Баннер"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("продукт"))
    name = models.CharField(max_length=255, verbose_name=_("название"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    image = models.ImageField(upload_to="static/img/banner", verbose_name=_("баннер"))
    is_active = models.BooleanField(default=False, verbose_name=_("активный"))

# Create your models here.
