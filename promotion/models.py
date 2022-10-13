from timestamps.models import models, Timestampable
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Banner(Timestampable):
    """Баннер"""

    from product.models import Product

    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name=_("продукт"))
    name = models.CharField(max_length=255, verbose_name=_("название"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    image = models.ImageField(upload_to="banner/%Y/%m/%d", verbose_name=_("баннер"))
    is_active = models.BooleanField(default=False, verbose_name=_("активный"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("баннер")
        verbose_name_plural = _("баннеры")


class DiscountType(Timestampable):
    """Тип акции"""

    description = models.CharField(max_length=512, verbose_name=_("описание"))

    class Meta:
        verbose_name = _("тип акции")
        verbose_name_plural = _("типы акций")
        managed = True

    def __str__(self):
        return self.description


class PromotionOffer(Timestampable):
    """Акция"""

    from product.models import Offer

    name = models.CharField(max_length=255, verbose_name=_("название"))
    description = models.CharField(max_length=255, verbose_name=_("описание"))
    discount_type_value = models.PositiveIntegerField(verbose_name=_("значение правила акции"))
    discount_decimals = models.DecimalField(default=0, max_digits=11, decimal_places=2, verbose_name=_("скидка"))
    discount_percentage = models.PositiveIntegerField(default=0, verbose_name="%")
    is_active = models.BooleanField(default=False, verbose_name=_("активная"))
    discount_type_id = models.ForeignKey(DiscountType, on_delete=models.DO_NOTHING, verbose_name=_("тип акции"))
    image = models.ImageField(blank=True, upload_to="shop_logo/%Y/%m/%d", verbose_name=_("фото"))
    offer = models.ManyToManyField(Offer, verbose_name=_('предложения'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("promotion-page", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("акция")
        verbose_name_plural = _("акции")
        managed = True
