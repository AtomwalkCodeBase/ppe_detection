import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

def send_alert(subject: str, message: str):
    try:
        email = Mail(
            from_email=os.getenv("ALERT_FROM_EMAIL"),
            to_emails=os.getenv("ALERT_TO_EMAIL"),
            subject=subject,
            plain_text_content=message
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(email)
        print("Alert email sent")

    except Exception as e:
        print("Email error:", e)
