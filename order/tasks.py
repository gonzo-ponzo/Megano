from django.conf import settings
from django.db import transaction, DatabaseError
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from .services import PaymentApi, CheckoutDB, OrderPaymentCache


@shared_task(bind=True, name="update_order_after_payment")
def update_order_after_payment(self, order_id: int) -> str:
    data, status = PaymentApi.get(order_id)

    if status:
        try:
            with transaction.atomic():
                order = CheckoutDB.set_order_payment(data)
        except DatabaseError as ex:
            status = False
            data = ex

    if status:
        result = f"Good order({order_id}): {data}"
    else:
        try:
            raise self.retry(max_retries=settings.CELERY_MAX_RETRIES_ORDER, countdown=settings.CELERY_COUNTDOWN_ORDER)
        except MaxRetriesExceededError as ex:
            order = CheckoutDB.set_order_status_max_retry(order_id)
            data = ex
        result = f"Bad order({order_id}): {data}"

    OrderPaymentCache.clean_data_from_cache(order.id, order.user_id)
    return result
