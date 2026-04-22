from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def send_contact_email(data):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = sender_email   # you receive message
    msg["Subject"] = data.subject

    body = f"""
New Message from Portfolio 🚀

Name: {data.name}
Email: {data.email}

Message:
{data.message}
"""

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()





def send_otp_email(to_email, otp, subject):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    body = f"""
Your OTP Code 🔐

OTP: {otp}

This OTP is valid for 5 minutes.
"""

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ OTP email sent")
    except Exception as e:
        print(f"❌ Email error: {e}")
        raise e