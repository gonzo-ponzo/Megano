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
        

@csrf_exempt
def api_one_bill(request, order_number):  # TODO совместить два метода, обрабатывать в зависимости от пост или гет-запрос
    """ (гет-запрос) в параметрах - номер счета,
    возвращается json с текущим статусом счета в очереди, если этот счет найден в очереди, либо ошибка"""
    """ (пост-запрос) в параметрах - номер счета, сумма к оплате, номер карты
    возвращается текущий статус счета в очереди (то есть должен быть нулевой)"""
    # при любом запросе - сначала ищем последний счет с нужным номером
    # для гет-запроса, возращаем найденный счет, либо возвращаем ошибку если счет не найден
    bill = Payment.objects.filter(order_number=order_number).order_by("-id").first()
    if request.method == "GET":
        if bill:
            # return JsonResponse({"order_number": bill.order_number, "status": bill.status, "status_text": bill.get_status_text()})
            return JsonResponse(PaymentSerializer(bill).data)
        else:
            return JsonResponse({"error": "Счет не найден"})
    else:
        # для пост-запроса - если статус счета был 0 или 1, то возвращаем такую или такую ошибку (подождите, пока оплатится предыдущий счет, либо счет уже оплачен)
        # если при пост-запросе счет отсутствует либо статус больше 1, тогда добавляем в таблицу новые данные, возвращаем информацию об этой записи в очереди
        if bill and bill.status == 0:
            return JsonResponse({"error": "Счет уже в очереди на оплату, дождитесь окончания процесса"})
        if bill and bill.status == 1:
            return JsonResponse({"error": "Счет уже оплачен"})
        print(request.POST)  # TODO не забыть убрать
        card_number = request.POST.get("card_number")
        sum_to_pay = request.POST.get("sum_to_pay")
        if card_number and sum_to_pay and Decimal(sum_to_pay) > 0:
            new_bill = Payment.objects.create(order_number=order_number, card_number=card_number, sum_to_pay=Decimal(sum_to_pay))
            return JsonResponse(PaymentSerializer(new_bill).data)
        else:
            return JsonResponse({"error": "Некорректные входные данные"})


def api_pay_all_bills(request):
    """ параметров - нет,
    возвращается json со списком статусов всех вы олненных во время запроса операций"""
    return JsonResponse({'done': False})  # return JsonResponse(PaymentSerializer(bills, many=True).data)
