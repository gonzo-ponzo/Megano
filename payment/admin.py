from django.contrib import admin

# TODO этой таблицы потом не должно быть в админке
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order_number", "card_number", "sum_to_pay", "status"]
