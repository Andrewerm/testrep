# Create your tasks here
from celery import shared_task
from services.utils import handle_myownstore

@shared_task
def task_handle_myownstore():
    handle_myownstore()

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


