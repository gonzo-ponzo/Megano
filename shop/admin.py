from django.contrib import admin
from .models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "phone",
        "email",
        "address",
        "created_at",
        "updated_at",
        "user"
    )
    list_display_links = ("id", "name")
    search_fields = ("name",)
    fields = (
        "name",
        "phone",
        "email",
        "address",
        "description",
        "image",
        "user",
        "created_at",
        "updated_at"
    )
    readonly_fields = ("created_at", "updated_at")
