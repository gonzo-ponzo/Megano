from payment.celery import app
import time
from .models import Process


@app.task(name="shop_import", track_started=True)
def shop_import(file_names, pr_name):
    from .services import one_shop_import
    for file_name in file_names:
        is_ok, message = one_shop_import(file_name)
        # TODO писать в логи нужное, переносить файл в соответствующую папку
        print(is_ok, message)
    process = Process.objects.get_or_create(name=pr_name)
    process.is_run = False
    process.save()
    return "import done"
