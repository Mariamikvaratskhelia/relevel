from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import ContactMessage


@shared_task
def send_contact_notification(message_id: int) -> None:
    msg = ContactMessage.objects.get(pk=message_id)
    send_mail(
        subject=f"New contact message from {msg.name}",
        message=f"{msg.message}\n\nReply to: {msg.email}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.CONTACT_RECIPIENT],
    )
