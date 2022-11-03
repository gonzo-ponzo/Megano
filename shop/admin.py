from django.contrib import admin
from .models import Shop, ShopImage
from django.utils.safestring import mark_safe


class ShopImageInLine(admin.TabularInline):
    model = ShopImage
    fields = ("get_image", "image", "created_at", "updated_at")
    readonly_fields = ("get_image", "created_at", "updated_at")
    extra = 0

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="150">')
        return "-"


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "address", "created_at", "updated_at", "user")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    fields = ("name", "phone", "email", "address", "description", "image", "user", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ShopImageInLine, ]

    def delete_queryset(self, request, queryset):
        queryset.update(email=None, phone=None)
        queryset.delete()
