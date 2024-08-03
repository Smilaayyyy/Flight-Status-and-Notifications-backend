import smtplib
from email.mime.text import MIMEText
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email(recipient, subject, body):
    """Send an email notification."""
    sender = '20cse062@gweca.ac.in'
    password = 'lvgl iwso eomw zcpv'.replace('\xa0', ' ')
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        logging.info(f"Sent email to {recipient}")
    except Exception as e:
        logging.error(f"Failed to send email to {recipient}: {e}")

