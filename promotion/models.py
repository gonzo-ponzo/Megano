from timestamps.models import models, Timestampable
from django.utils.translation import gettext_lazy as _

from product.models import Product


class Banner(Timestampable):
    """Баннер"""

    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("продукт"))
    name = models.CharField(max_length=255, verbose_name=_("название"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    image = models.ImageField(upload_to="banner/%Y/%m/%d", verbose_name=_("баннер"))
    is_active = models.BooleanField(default=False, verbose_name=_("активный"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("баннер")
        verbose_name_plural = _("баннеры")
