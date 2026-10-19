"""Explicitly configured adapter; no notifications run from the API or tests."""
import os
import smtplib
from email.message import EmailMessage


class NotificationService:
    def __init__(self, host=None, port=587, username=None, password=None, sender=None, transport=smtplib.SMTP):
        self.host, self.port = host, port
        self.username, self.password, self.sender = username, password, sender
        self.transport = transport

    @classmethod
    def from_environment(cls):
        return cls(host=os.getenv('SMTP_HOST'), port=int(os.getenv('SMTP_PORT', '587')),
                   username=os.getenv('SMTP_USERNAME'), password=os.getenv('SMTP_PASSWORD'), sender=os.getenv('SMTP_SENDER'))

    def send_email(self, recipient, subject, body):
        if not all((self.host, self.username, self.password, self.sender)):
            raise RuntimeError('SMTP must be configured explicitly')
        message = EmailMessage(); message['From'] = self.sender; message['To'] = recipient
        message['Subject'] = subject; message.set_content(body)
        with self.transport(self.host, self.port, timeout=10) as connection:
            connection.starttls(); connection.login(self.username, self.password); connection.send_message(message)
