from timestamps.models import models, Model, Timestampable
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from shop.models import Shop

User = get_user_model()


class Product(Model):
    """Продукт"""

    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    limited = models.BooleanField(default=False, verbose_name=_("ограниченный тираж"))
    manufacturer = models.ForeignKey("Manufacturer", on_delete=models.PROTECT, verbose_name=_("производитель"))
    category = models.ForeignKey("ProductCategory", on_delete=models.PROTECT, verbose_name=_("категория"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))
    shop = models.ManyToManyField(Shop, through="Offer", verbose_name=_("магазины"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("продукт")
        verbose_name_plural = _("продукты")


class Offer(Model):
    """Предложение магазина"""

    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, verbose_name=_("магазин"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("продукт"))
    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("цена"))
    amount = models.PositiveIntegerField(verbose_name=_("количество"))

    class Meta:
        verbose_name = _("предложение магазина")
        verbose_name_plural = _("предложения магазина")


class ProductImage(Timestampable):
    """Картинка продукта"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("продукт"))
    image = models.ImageField(upload_to="product/%Y/%m/%d", verbose_name=_("фото"))

    class Meta:
        verbose_name = _("картинка продукта")
        verbose_name_plural = _("картинки продукта")


class ProductCategory(MPTTModel, Model):
    """Категория продукта"""

    name = models.CharField(max_length=512, verbose_name=_("название"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    icon = models.ImageField(upload_to="category/%Y/%m/%d", verbose_name=_("значок"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name="url")
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="children")

    def __str__(self):
        return self.name

    class MPTTMeta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")
        order_insertion_by = ["id"]


class Property(Timestampable):
    """Свойство продукта"""

    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.TextField(blank=True, verbose_name=_("описание"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("свойство продукта")
        verbose_name_plural = _("свойства продукта")


class ProductProperty(Timestampable):
    """Значение свойства продукта"""

    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("продукт"))
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name=_("свойство"))
    value = models.CharField(max_length=128, verbose_name=_("значение"))

    class Meta:
        verbose_name = _("значение свойства продукта")
        verbose_name_plural = _("значения свойства продукта")


class Manufacturer(Model):
    """Производитель"""

    name = models.CharField(max_length=255, verbose_name=_("название"))
    logo = models.ImageField(blank=True, upload_to="manufacturer/%Y/%m/%d", verbose_name=_("логотип"))
    description = models.TextField(blank=True, verbose_name=_("описание"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("производитель")
        verbose_name_plural = _("производители")


class Review(Timestampable):
    """Отзыв"""

    MIN_GRADE = 1
    MAX_GRADE = 5
    GRADE_CHOICES = [(grade, grade) for grade in range(MIN_GRADE, MAX_GRADE + 1)]

    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("продукт"))
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("пользователь"))
    text = models.TextField(verbose_name=_("текст"))
    rating = models.IntegerField(choices=GRADE_CHOICES, verbose_name=_("рейтинг"))

    class Meta:
        verbose_name = _("отзыв")
        verbose_name_plural = _("отзывы")


class ProductView(Model):
    """Список просмотренных продуктов"""

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("пользователь"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("продукт"))

    class Meta:
        verbose_name = _("просмотренный продукт")
        verbose_name_plural = _("просмотренные продукты")
