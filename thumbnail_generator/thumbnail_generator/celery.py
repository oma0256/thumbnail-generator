import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thumbnail_generator.settings')

app = Celery('thumbnail_generator')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
