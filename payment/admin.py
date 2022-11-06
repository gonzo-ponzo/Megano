from django.contrib import admin
from django_celery_results.models import TaskResult
from django_celery_results.admin import TaskResultAdmin

from .models import Payment  # TODO этой таблицы потом не должно быть в админке


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order_number", "card_number", "sum_to_pay", "status"]


class CustomTaskResultAdmin(TaskResultAdmin):
    list_display = ("task_id", "task_name", "date_done",
                    "status", "result")


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)
