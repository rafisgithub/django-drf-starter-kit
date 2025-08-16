from django.core.mail import EmailMessage, get_connection
from apps.system_setting.models import SMTPSetting

class SMTPMailer:
    def __init__(self):
        self.smtp_config = SMTPSetting.objects.filter(is_active=True).first()
        if not self.smtp_config:
            raise Exception("No active SMTP configuration found.")

    def get_connection(self):
        backend_settings = self.smtp_config.get_email_backend_settings()
        return get_connection(
            host=backend_settings['EMAIL_HOST'],
            port=backend_settings['EMAIL_PORT'],
            username=backend_settings['EMAIL_HOST_USER'],
            password=backend_settings['EMAIL_HOST_PASSWORD'],
            use_tls=backend_settings['EMAIL_USE_TLS'],
            use_ssl=backend_settings['EMAIL_USE_SSL'],
        )

    def send_email(self, subject, body, to_emails, from_email=None, html_body=None, attachments=None):
        """
        Send an email using the active SMTP settings.

        Parameters:
        - subject: email subject (string)
        - body: plain text email body (string)
        - to_emails: list of recipient emails (list of strings)
        - from_email: override sender email (string), optional
        - html_body: html content (string), optional
        - attachments: list of (filename, content, mimetype), optional
        """
        if from_email is None:
            from_email = f"{self.smtp_config.sender_name or ''} <{self.smtp_config.sender_email}>"

        connection = self.get_connection()

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to_emails,
            connection=connection,
        )

        if html_body:
            email.content_subtype = 'html'
            email.body = html_body

        if attachments:
            for filename, content, mimetype in attachments:
                email.attach(filename, content, mimetype)

        email.send()
