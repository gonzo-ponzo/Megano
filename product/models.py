from timestamps.models import models, Model, Timestampable
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from shop.models import Shop

User = get_user_model()


class Product(Model):
    """Продукт"""

    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    limited = models.BooleanField(default=False, verbose_name=_("ограниченный тираж"))
    manufacturer = models.ForeignKey("Manufacturer", on_delete=models.DO_NOTHING, verbose_name=_("производитель"))
    category = TreeForeignKey("ProductCategory", on_delete=models.DO_NOTHING, verbose_name=_("категория"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))
    shop = models.ManyToManyField(Shop, through="Offer", verbose_name=_("магазины"))

    def get_absolute_url(self):
        return reverse("product-page", kwargs={"pk": self.pk})

    def get_attributes(self):
        return {k.property: k for k in self.productproperty_set.all()}

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("продукт")
        verbose_name_plural = _("продукты")


class Offer(Model):
    """Предложение магазина"""

    shop = models.ForeignKey(Shop, on_delete=models.DO_NOTHING, verbose_name=_("магазин"))
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name=_("продукт"))
    price = models.DecimalField(max_digits=11, decimal_places=2, verbose_name=_("цена"))
    amount = models.PositiveIntegerField(verbose_name=_("количество"))

    def __str__(self):
        return f"{self.shop} - {self.product}"

    class Meta:
        verbose_name = _("предложение магазина")
        verbose_name_plural = _("предложения магазина")


class ProductImage(Timestampable):
    """Изображение продукта"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("продукт"))
    image = models.ImageField(upload_to="product/%Y/%m/%d", verbose_name=_("фото"))

    class Meta:
        verbose_name = _("изображение продукта")
        verbose_name_plural = _("изображения продукта")


class TreeSoftDeleteManager(TreeManager):
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True)


class ProductCategory(MPTTModel, Model):
    """Категория продукта"""

    objects = TreeSoftDeleteManager()

    name = models.CharField(max_length=512, verbose_name=_("название"))
    description = models.TextField(blank=True, verbose_name=_("описание"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name="url")
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("родительская категория"),
    )

    @classmethod
    def with_active_products_count(cls):
        return cls.objects.add_related_count(
            cls.objects, Product, "category", "products_cumulative_count", cumulative=True
        )

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        super().delete()

        if not self.is_leaf_node():
            children = self.get_descendants()
            for child in children:
                child.deleted_at = self.deleted_at
            ProductCategory.objects.bulk_update(children, fields=["deleted_at"])

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")


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

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("продукт"))
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


class Review(Model):
    """Отзыв"""

    MIN_GRADE = 1
    MAX_GRADE = 5
    GRADE_CHOICES = [(grade, grade) for grade in range(MIN_GRADE, MAX_GRADE + 1)]

    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name=_("продукт"))
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("пользователь"))
    text = models.TextField(verbose_name=_("текст"))
    rating = models.PositiveSmallIntegerField(choices=GRADE_CHOICES, verbose_name=_("рейтинг"))

    class Meta:
        verbose_name = _("отзыв")
        verbose_name_plural = _("отзывы")


class ProductView(Model):
    """Список просмотренных продуктов"""

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name=_("пользователь"))
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, verbose_name=_("продукт"))

    class Meta:
        verbose_name = _("просмотренный продукт")
        verbose_name_plural = _("просмотренные продукты")
        ordering = ["-created_at"]
