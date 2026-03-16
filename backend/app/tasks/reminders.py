from celery import Celery
from app.config import settings
from app.services.email import send_email

celery_app = Celery("devtrack", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


@celery_app.task
def send_reminder_email(reminder_id: int, user_email: str, message: str):
    """Celery task: send a reminder email at the scheduled time."""
    send_email(
        to=user_email,
        subject="DevTrack Reminder",
        body=f"Reminder: {message}",
    )
