from .celery import app
from .models import Payment
from .services import Pay


@app.task(name="pay_actual_bills")
def pay_actual_bills():
    curr_payments = Payment.objects.filter(status=0)
    res_ok, res_fail = 0, 0
    for payment in curr_payments:
        if Pay.pay(payment):
            res_ok += 1
        else:
            res_fail += 1
    return f"{res_ok} ok, {res_fail} fail"
