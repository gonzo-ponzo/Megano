from django.contrib import admin
from .models import Order, OrderOffer, Delivery


class OrderOfferInLine(admin.TabularInline):
    model = OrderOffer
    fk_name = "order"
    fields = ("offer", "price", "amount", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "city", "address", "status_type", "error_type", "created_at", "updated_at")
    list_display_links = ("id", "user")
    search_fields = ("user",)
    fields = ("user", "delivery_type", "payment_type", "city", "address", "comment",
              "status_type", "error_type", "created_at", "updated_at")
    readonly_fields = ("error_type", "created_at", "updated_at")
    inlines = (OrderOfferInLine, )
    save_on_top = True


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "price", "express_price", "sum_order", "created_at", "updated_at")
    list_display_links = ("id",)
    fields = ("price", "express_price", "sum_order", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
