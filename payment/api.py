from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework import serializers
from decimal import Decimal

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    status_text = serializers.ReadOnlyField(source="get_status_text")

    class Meta:
        model = Payment
        fields = ["order_number", "status", "status_text"]


def check_correct_Decimal(str_number):
    if str_number:
        res = Decimal(str_number)
        if int(res*100) < res*100:  # в числе больше двух десятичных знаков
            return 0
        return res
    return 0


@csrf_exempt
def api_one_bill(request, order_number):
    """
    (гет-запрос) в параметрах - номер счета,
    (пост-запрос) корректные входные данные: номер счета, сумма к оплате (положительное
     число, не больше двух знаков после запятой), номер карты;
    возвращается сериализованная запись об оплате счета, либо ошибка"""
    bill = Payment.objects.filter(order_number=order_number).order_by("-id").first()
    if request.method == "GET":
        if bill:
            return JsonResponse(PaymentSerializer(bill).data)
        else:
            return JsonResponse({"error": "Счет не найден"})
    else:
        if bill and bill.status == 0:
            return JsonResponse({"error": "Счет уже в очереди на оплату, дождитесь окончания процесса"})
        if bill and bill.status == 1:
            return JsonResponse({"error": "Счет уже оплачен"})
        card_number = request.POST.get("card_number")
        sum_to_pay = check_correct_Decimal(request.POST.get("sum_to_pay"))
        if card_number and sum_to_pay > 0:
            new_bill = Payment.objects.create(order_number=order_number,
                                              card_number=card_number, sum_to_pay=sum_to_pay)
            # (может быть, стоит перед отправкой ответа обновить данные из базы данных)
            return JsonResponse(PaymentSerializer(new_bill).data)
        else:
            return JsonResponse({"error": "Некорректные входные данные"})


def api_pay_all_bills(request):
    """ параметров - нет,
    возвращается json со списком статусов всех вы олненных во время запроса операций"""
    return JsonResponse({'done': False})  # return JsonResponse(PaymentSerializer(bills, many=True).data)
