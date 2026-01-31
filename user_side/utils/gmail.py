# utils/email_utils.py
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings


def get_gmail_service():
    creds = Credentials(
        None,
        refresh_token=settings.GMAIL_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    return build("gmail", "v1", credentials=creds)


def send_email_via_gmail(to_email, subject, html_content):
    service = get_gmail_service()
    message = MIMEText(html_content, "html")
    message["to"] = to_email
    message["from"] = settings.GMAIL_SENDER_EMAIL
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()


###########################   send otp to user email   ########################################

def send_otp_email(to_email, otp, username="User", purpose="OTP Verification"):
    """
    Sends a styled OTP email for any purpose: signup, email change, password change, forget password.
    """
    subject = f"Your {purpose} Code"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f6f8fa; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background-color: #ffffff; padding: 25px; border-radius: 8px;">
            <h2 style="color: #1cc0a0; text-align: center;">
                Cycular Verification Code
            </h2>
            <p style="font-size: 15px; color: #333;">
                Dear <strong>{username}</strong>,
            </p>
            <p style="font-size: 15px; color: #333;">
                You requested a verification code for <strong>{purpose}</strong>. Please use the following One-Time Password (OTP):
            </p>
            <div style="
                text-align: center;
                font-size: 28px;
                letter-spacing: 4px;
                font-weight: bold;
                color: #1cc0a0;
                margin: 20px 0;
                padding: 12px;
                border: 2px dashed #1cc0a0;
                border-radius: 6px;">
                {otp}
            </div>
            <p style="font-size: 14px; color: #555;">
                This OTP is valid for <strong>5 minutes</strong>. Please do not share this code with anyone.
            </p>
            <p style="font-size: 14px; color: #555;">
                If you did not request this OTP, you can safely ignore this email.
            </p>
            <hr style="border: none; border-top: 1px solid #eaeaea; margin: 20px 0;">
            <p style="font-size: 13px; color: #777; text-align: center;">
                Regards,<br>
                <strong style="color:#1cc0a0;">The Cycular Team</strong>
            </p>
        </div>
    </body>
    </html>
    """

    send_email_via_gmail(to_email=to_email, subject=subject, html_content=html_content)
