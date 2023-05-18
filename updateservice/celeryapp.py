from celery import Celery
from datetime import timedelta
from updateservice.settings import setting

app = Celery('tasks', broker=setting["broker_url"], include=["updateservice.tasks"])

app.conf.beat_schedule = {
    'run-every-30-seconds': {
        'task': 'tasks.backup_task',
        'schedule': timedelta(seconds=30),
    },
}