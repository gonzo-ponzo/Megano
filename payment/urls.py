from django.urls import path
from .api import api_one_bill, api_pay_all_bills


urlpatterns = [
    path("", api_pay_all_bills, name="all_payments"),  # TODO если этого метода тут не надо, то убрать файл urls
    path("<int:order_number>", api_one_bill, name="one_payment"),
]
