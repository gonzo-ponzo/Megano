from celery import Celery

from .models import Payment
from .services import Pay


app = Celery('payment', broker='redis://redis_db')

@app.task
def pay_actual_bills():
    curr_payments = Payment.objects.filter(status=0)
    for payment in curr_payments:
        Pay.pay(payment)
    return
