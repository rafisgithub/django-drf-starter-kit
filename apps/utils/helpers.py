# utils/api_response.py

from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives


def success(data=None, message="Success", status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)

def error(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status_code)



def send_email(subject, body, to_emails, from_email=None, html_body=None, attachments=None):
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to_emails,
        headers={'X-Requested-With': 'XMLHttpRequest'}

    )

    if attachments:
        for attachment in attachments:
            email.attach(attachment['filename'], attachment['content'], attachment['mimetype'])
    
    if html_body:
        email.attach_alternative(html_body, "text/html")    
    # Send the email
    email.send()