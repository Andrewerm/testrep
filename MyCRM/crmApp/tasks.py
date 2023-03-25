# Create your tasks here
from MyCRM.celery import app
from celery import shared_task
from services.utils import handle_myownstore, handle_AvangardProducts
import datetime

@shared_task
def task_handle_myownstore():
    handle_myownstore()

@shared_task
def task_handle_avangardstore():
    handle_AvangardProducts()


@shared_task(bind=True, default_retry_delay=5*60)
def add(self, x, y):
    try:
        return x + y
    except Exception as exc:
        print(f'ошибка {exc}')
        raise self.retry(exc=exc,countdown=60)


@app.task(bind=True, default_retry_delay=5*60)
def mul(self, x, y):
    return x + y


@shared_task
def xsum(numbers):
    return sum(numbers)

@app.task
def saveToFile(params):
        with open('testing.txt', 'a') as f:
            t = datetime.datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
            f.write(f'{t} - {params} \n')

