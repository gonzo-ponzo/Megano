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

    get_image.short_description = "миниатюра"


@admin.register(PromotionOffer)
class PromotionOfferAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "discount_type_value", "discount_decimals", "discount_percentage", "is_active", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    filter_horizontal = ("offer", )
    fields = ("name", "discount_type_value", "discount_decimals", "discount_percentage", "is_active", "discount_type_id", "image", "offer")
    readonly_fields = ("created_at", "updated_at")
    actions = ["make_active", "make_inactive"]

    @admin.action(description=_("Активировать"))
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_("Деактивировать"))
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(DiscountType)
class DiscountTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "created_at", "updated_at")
    list_display_links = ("id", "description")
    search_fields = ("id", "description")
    fields = ("description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
