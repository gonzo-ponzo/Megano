from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Product, ProductCategory, Manufacturer, Offer, Review, Property, ProductProperty, ProductImage


class OfferInLine(admin.TabularInline):
    model = Offer
    fk_name = "product"
    fields = ("shop", "price", "amount", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    extra = 1


class ProductPropertyInLine(admin.TabularInline):
    model = ProductProperty
    fk_name = "product"
    fields = ("property", "value", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    extra = 1


class ProductImageInLine(admin.TabularInline):
    model = ProductImage
    fields = ("get_image", "image", "created_at", "updated_at")
    readonly_fields = ("get_image", "created_at", "updated_at")
    extra = 1

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150">')
        return "-"

    get_image.short_description = _("фото")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "manufacturer", "category", "limited", "created_at", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name", "category__name")
    list_filter = ("category",)
    fields = ("name", "manufacturer", "category", "limited", "description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = (ProductImageInLine, ProductPropertyInLine, OfferInLine)
    save_on_top = True
    actions = ["make_limited", "make_unlimited"]

    @admin.action(description=_("сделать ограниченный тираж"))
    def make_limited(self, request, queryset):
        queryset.update(limited=True)

    @admin.action(description=_("отменить ограниченный тираж"))
    def make_unlimited(self, request, queryset):
        queryset.update(limited=False)


@admin.register(ProductCategory)
class ProductCategoryAdmin(MPTTModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "id", "slug", "created_at", "updated_at", "related_products_cumulative_count")
    list_display_links = ("name", "id")
    search_fields = ("name",)
    fields = ("name", "slug", "parent", "description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        return ProductCategory.with_active_products_count()

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count

    related_products_cumulative_count.short_description = _("количество продуктов")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    fields = ("name", "description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    fields = ("name", "logo", "description", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "rating", "text_short", "user", "created_at")
    list_display_links = ("id", "product")
    search_fields = ("product__name",)
    fields = ("product", "rating", "text", "user", "created_at")
    readonly_fields = ("created_at",)
    save_as = True

    @staticmethod
    def text_short(obj):
        return f"{obj.text[:20]}..."
