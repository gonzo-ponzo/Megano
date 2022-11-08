from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Banner, PromotionOffer, DiscountType


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "product", "get_image", "is_active", "created_at", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name", "product__name")
    fields = ("name", "product", "description", "get_image", "image", "is_active", "created_at", "updated_at")
    readonly_fields = ("get_image", "created_at", "updated_at")
    actions = ["make_active", "make_inactive"]

    @admin.action(description=_("сделать активным(и)"))
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_("сделать неактивным(и)"))
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150">')
        return "-"

    get_image.short_description = _("миниатюра")


@admin.register(PromotionOffer)
class PromotionOfferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "discount_type_value",
        "discount_decimals",
        "discount_percentage",
        "is_active",
        "updated_at",
    )
    list_display_links = ("id", "name")
    search_fields = ("name",)
    filter_horizontal = ("offer",)
    fields = (
        "name",
        "discount_type_id",
        "discount_type_value",
        "discount_decimals",
        "discount_percentage",
        "is_active",
        "image",
        "offer",
    )
    readonly_fields = ("created_at", "updated_at")
    actions = ["make_active", "make_inactive"]

    @admin.action(description=_("Активировать"))
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_("Деактивировать"))
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["discount_type_value"].help_text = """
        Значение (N) для типа акции, при котором текущая акция будет формировать скидку.
        """
        form.base_fields["discount_decimals"].help_text = """
        Если не указано - расчет идет по процентам.
        """
        form.base_fields["discount_percentage"].help_text = """
        Расчет по процентам только в том случае, если не указана фиксированная скидка в рублях.
        """
        form.base_fields["offer"].label = """
        Выберите предложения, на которые будет распростроняться скидка
        """
        return form


@admin.register(DiscountType)
class DiscountTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "created_at", "updated_at")
    list_display_links = ("id", "description")
    search_fields = ("id", "description")
    fields = ("description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
