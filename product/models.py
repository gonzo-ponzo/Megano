from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """Продукт"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))


class Property(models.Model):
    """Свойство продукта"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))


class ProductProperty(models.Model):
    """Значение свойства продукта"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    value = models.CharField(max_length=128, verbose_name=_("значение"))
