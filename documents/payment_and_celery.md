# API payment

## добавить счет на оплату - POST-запрос такого вида:
    url = reverse("one_payment", args=[<номер_счета>])
    data = {"card_number": "<номер_карты>", "sum_to_pay": <сумма_к_оплате>}
    response = self.client.post(url, data)
Возвращается либо json с полями ["order_number", "status", "status_text"], если счет успешно поставлен в очередь. Либо json с ключом "error", если в очереди уже есть счет с таким же номером, новый либо оплаченный.

## проверить статус счета - GET-запрос:
    url = reverse("one_payment", args=[<номер_счета>])
    response = self.client.get(url)
Возвращается либо json с полями ["order_number", "status", "status_text"], если запись об искомом счете есть в очереди, либо json с ключом "error".

### Статусы платежей
* 0 - новый платеж
* 1 - оплата успешна
* 2,3,4 и выше - платеж не прошел, по какой-либо причине

---
# CELERY для обработки платежей

В requirements новые пакеты, в payment/fixtures - файл с задачей в расписании celery.

Для запуска обработчика событий можно использовать команду (внутри контейнера с кодом):
`celery -A payment worker --beat --scheduler django --loglevel=info`

Для экспериментов - добавлять новые записи [тут](http://127.0.0.1:8000/admin/payment/payment/), и смотреть как celery будет им статусы менять.

