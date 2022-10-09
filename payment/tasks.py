from .celery import app
from .models import Payment
from .services import Pay


@app.task(name="pay_actual_bills")
def pay_actual_bills():
    curr_payments = Payment.objects.filter(status=0)
    for payment in curr_payments:
        Pay.pay(payment)
    return
