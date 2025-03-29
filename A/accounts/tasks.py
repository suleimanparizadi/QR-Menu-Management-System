from .models import OTPcode
from celery import shared_task
from django.utils import timezone


@shared_task
def remove_expired_otps():
    now = timezone.now()
    expired_opts = OTPcode.objects.filter(created_at__lt=now)
    expired_opts.delete()