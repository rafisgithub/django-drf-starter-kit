import secrets
from django.core.mail import EmailMessage
from django.conf import settings

def generate_otp(length=6):
    digits = '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))

def send_normal_mail(data):
    email = EmailMessage(
        subject=data['subject'],
        body=data['body'],
        from_email=settings.EMAIL_HOST_USER,
        to=data['to']
    )
    email.send()