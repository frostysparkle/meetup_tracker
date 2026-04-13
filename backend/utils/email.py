import smtplib
from email.message import EmailMessage
import os
import threading
import traceback
import streamlit as st

def send_email_async(to_email: str, subject: str, body: str, attachment_bytes: bytes = None):
    """Sends an email in a background thread."""
    
    smtp_email = os.environ.get("SMTP_EMAIL")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_email or not smtp_password or smtp_email == "your_email@example.com":
        print("SMTP credentials not configured. Skipping email send.")
        return

    def _send():
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = smtp_email
            msg['To'] = to_email

            if attachment_bytes:
                msg.add_attachment(attachment_bytes, maintype='image', subtype='png', filename='ticket.png')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: # Assuming Gmail, configurable if needed
                server.login(smtp_email, smtp_password)
                server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            traceback.print_exc()

    thread = threading.Thread(target=_send)
    thread.start()
