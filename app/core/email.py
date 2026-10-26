import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

def send_verification_email_sync(recipient_email: str, code: str, user_name: str = "Friend") -> bool:
    """
    Sends a clean, simple, uncolored verification email with the 6-digit OTP code using Gmail SMTP_SSL.
    No heavy color backgrounds or complex cards - simple, clear, and easy to read.
    """
    try:
        clean_password = settings.SMTP_PASSWORD.replace(" ", "")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"{code} is your Muraho verification code"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = recipient_email

        # Clean plaintext version
        text_body = f"""Hello {user_name},

Your verification code is: {code}

This code will expire in 10 minutes.

If you did not request this code, you can safely ignore this email.

Muraho
"""

        # Clean, simple, minimalist HTML without colored containers or dark themes
        html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Verification Code</title>
</head>
<body style="margin: 0; padding: 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #111827; background-color: #ffffff; line-height: 1.5;">
  <div style="max-width: 480px; margin: 0 auto;">
    <p style="font-size: 16px; margin: 0 0 16px 0;">Hello {user_name},</p>
    
    <p style="font-size: 15px; margin: 0 0 20px 0; color: #374151;">
      Your verification code is:
    </p>

    <div style="margin: 24px 0;">
      <span style="font-family: monospace, Courier; font-size: 32px; font-weight: 700; letter-spacing: 6px; color: #111827;">
        {code}
      </span>
    </div>

    <p style="font-size: 14px; color: #4b5563; margin: 0 0 16px 0;">
      This code will expire in 10 minutes.
    </p>

    <p style="font-size: 13px; color: #6b7280; margin: 24px 0 0 0; border-top: 1px solid #e5e7eb; padding-top: 16px;">
      If you did not request this verification code, please ignore this email.
    </p>
  </div>
</body>
</html>
"""
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Connect with SSL on port 465
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
            server.login(settings.SMTP_USER, clean_password)
            server.send_message(msg)
        
        print(f"[Muraho Email] Successfully dispatched clean verification email with code {code} to {recipient_email}")
        return True
    except Exception as e:
        print(f"[Muraho Email] Failed to send email to {recipient_email}: {type(e).__name__} - {e}")
        return False

async def send_verification_email(recipient_email: str, code: str, user_name: str = "Friend") -> bool:
    """
    Asynchronous non-blocking wrapper to send verification email.
    """
    return await asyncio.to_thread(send_verification_email_sync, recipient_email, code, user_name)
