from payment.celery import app
import time
from .models import Process
# from .services import Pay


@app.task(name="shop_import", track_started=True)
def shop_import(file_names, pr_name):
    print(f"HI from future import, file_names = {file_names}")
    time.sleep(5*60)
    print("and Bye")
    process = Process.objects.get(name=pr_name)
    process.is_run = False
    process.save()
    return "import done"
