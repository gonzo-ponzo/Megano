from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "product", "get_image", "is_active", "created_at", "updated_at")
    list_display_links = ("id", "name")
    search_fields = ("name", "product__name")
    fields = ("name", "product", "description", "get_image", "image", "is_active", "created_at", "updated_at")
    readonly_fields = ("get_image", "created_at", "updated_at")
    actions = ['make_active', 'make_inactive']

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
