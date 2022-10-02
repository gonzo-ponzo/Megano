from celery import Celery

app = Celery('payment', broker='redis://redis_db')

@app.task
def add(x, y):
    # print(x / y)
    print("hello from Celery, write me up")
    return x + y
