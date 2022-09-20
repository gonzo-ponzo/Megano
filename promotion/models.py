from timestamps.models import models, Timestampable
from django.utils.translation import gettext_lazy as _
from django.db.models import Model
from shop.models import Shop


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
        verbose_name = _("Тип акции")
        verbose_name_plural = _("Типы акций")
        managed = True

    def __str__(self):
        return self.description


class PromotionOffer(Timestampable):
    """Акция"""
    from product.models import Offer
    name = models.CharField(max_length=255, verbose_name=_("название"))
    discount_type_value = models.PositiveIntegerField(verbose_name=_("Значение правила акции"))
    discount_decimals = models.PositiveIntegerField(default=0, verbose_name=_("Скидка"))
    discount_percentage = models.PositiveIntegerField(default=0, verbose_name=_("%"))
    is_active = models.BooleanField(default=False, verbose_name=_("активная"))
    discount_type_id = models.ForeignKey(DiscountType, on_delete=models.DO_NOTHING, verbose_name=_("Тип акции"))
    offer = models.ManyToManyField(Offer)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("акция")
        verbose_name_plural = _("акции")
        managed = True
