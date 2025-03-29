from celery import Celery
import os
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'A.settings')

celery_app = Celery('A')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedules = {
    'delete-expired-otp-codes-every-2-minutes':{
        'task':'accounts.tasks.remove_expired_otps',
        'schedules':crontab(minute='*/2'),
    }
}