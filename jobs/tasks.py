from payment.celery import app
import time
# from .models import Payment
# from .services import Pay


@app.task(name="shop_import", track_started=True)
def shop_import(p):
    print("HI from future import, p =", p)
    time.sleep(5*60)
    print("and Bye")
    return f"import done"
