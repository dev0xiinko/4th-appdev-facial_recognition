"""
email_service.py - Email Notification Service

This module handles sending email notifications to guardians
when students log in or out of the attendance system.

Configuration:
    Set the following environment variables or edit the config below:
    - SMTP_SERVER: SMTP server address
    - SMTP_PORT: SMTP server port
    - SMTP_EMAIL: Sender email address
    - SMTP_PASSWORD: Sender email password
    - SMTP_USE_TLS: Use TLS (true/false)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional
import threading

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
# You can set these as environment variables or edit directly here

SMTP_CONFIG = {
    "server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
    "port": int(os.environ.get("SMTP_PORT", "587")),
    "email": os.environ.get("SMTP_EMAIL", "alquizarkun@gmail.com"),  # Your email address
    "password": os.environ.get("SMTP_PASSWORD", "ynoi imrc oxaw rtkl "),  # App password for Gmail
    "use_tls": os.environ.get("SMTP_USE_TLS", "true").lower() == "true",
    "from_name": os.environ.get("SMTP_FROM_NAME", "Appdev Facial Recognition Attendance System")
}

# Enable/disable email sending (set to False to disable)
EMAIL_ENABLED = bool(SMTP_CONFIG["email"] and SMTP_CONFIG["password"])


def send_email_async(to_email: str, subject: str, html_body: str, text_body: str = None, image_path: str = None):
    """
    Send email asynchronously (non-blocking).
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of email
        text_body: Plain text content (optional)
        image_path: Path to image to embed (optional)
    """
    thread = threading.Thread(
        target=_send_email,
        args=(to_email, subject, html_body, text_body, image_path)
    )
    thread.daemon = True
    thread.start()


def _send_email(to_email: str, subject: str, html_body: str, text_body: str = None, image_path: str = None):
    """
    Send email synchronously.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of email
        text_body: Plain text content (optional)
        image_path: Path to image to embed (optional)
    """
    if not EMAIL_ENABLED:
        print(f"[EMAIL] Email disabled - would send to {to_email}: {subject}")
        return False
    
    if not to_email:
        print("[EMAIL] No recipient email provided")
        return False
    
    try:
        # Create message with mixed type to support both alternatives and attachments
        msg = MIMEMultipart("related")
        msg["Subject"] = subject
        msg["From"] = f"{SMTP_CONFIG['from_name']} <{SMTP_CONFIG['email']}>"
        msg["To"] = to_email
        
        # Create alternative part for text/html
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)
        
        # Add plain text version
        if text_body:
            part_text = MIMEText(text_body, "plain")
            msg_alternative.attach(part_text)
        
        # Add HTML version
        part_html = MIMEText(html_body, "html")
        msg_alternative.attach(part_html)
        
        # Attach image if provided
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                
                # Create image attachment with Content-ID for embedding
                img = MIMEImage(img_data)
                img.add_header('Content-ID', '<capture_image>')
                img.add_header('Content-Disposition', 'inline', filename='capture.jpg')
                msg.attach(img)
                
                print(f"[EMAIL] Image attached: {image_path}")
            except Exception as img_error:
                print(f"[EMAIL] Could not attach image: {img_error}")
        
        # Connect and send
        with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as server:
            if SMTP_CONFIG["use_tls"]:
                server.starttls()
            server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
            server.send_message(msg)
        
        print(f"[EMAIL] Sent to {to_email}: {subject}")
        return True
        
    except Exception as e:
        print(f"[EMAIL] Error sending to {to_email}: {str(e)}")
        return False


def send_attendance_notification(
    guardian_email: str,
    guardian_name: str,
    student_name: str,
    log_type: str,
    timestamp: datetime,
    year_level: str = None,
    image_path: str = None
) -> bool:
    """
    Send attendance notification email to guardian with captured image.
    
    Args:
        guardian_email: Guardian's email address
        guardian_name: Guardian's name
        student_name: Student's name
        log_type: "IN" or "OUT"
        timestamp: Time of the log
        year_level: Student's year level
        image_path: Path to the captured image
    
    Returns:
        bool: True if email was sent/queued successfully
    """
    if not guardian_email:
        print(f"[EMAIL] No guardian email for {student_name}")
        return False
    
    # Format timestamp
    time_str = timestamp.strftime("%I:%M %p")
    date_str = timestamp.strftime("%B %d, %Y")
    
    # Determine action text
    if log_type.upper() == "IN":
        action = "arrived at"
        action_emoji = "✅"
        action_color = "#00cc7a"
        status_text = "TIME IN"
    else:
        action = "left"
        action_emoji = "👋"
        action_color = "#f59e0b"
        status_text = "TIME OUT"
    
    # Email subject
    subject = f"{action_emoji} {student_name} - {status_text} | {time_str}"
    
    # Image section HTML - only add if image exists
    image_section = ""
    if image_path and os.path.exists(image_path):
        image_section = """
                    <!-- Captured Image -->
                    <tr>
                        <td style="padding: 0 30px 20px 30px;">
                            <p style="font-size: 14px; color: #666; margin: 0 0 10px 0; text-align: center;">
                                <strong>📷 Captured Photo:</strong>
                            </p>
                            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 10px;">
                                <img src="cid:capture_image" alt="Captured Photo" style="max-width: 100%; max-height: 300px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            </div>
                        </td>
                    </tr>
        """
    
    # HTML email body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <!-- Header -->
            <tr>
                <td style="background: linear-gradient(135deg, #0a0e14 0%, #1a2130 100%); padding: 30px; text-align: center;">
                    <h1 style="color: #00ff9d; margin: 0; font-size: 24px;"Appdev Facial Recognition Attendance</h1>
                    <p style="color: #8b949e; margin: 10px 0 0 0; font-size: 14px;">Attendance Notification</p>
                </td>
            </tr>
            
            <!-- Status Banner -->
            <tr>
                <td style="background-color: {action_color}; padding: 20px; text-align: center;">
                    <h2 style="color: white; margin: 0; font-size: 28px;">{action_emoji} {status_text}</h2>
                </td>
            </tr>
            
            <!-- Content -->
            <tr>
                <td style="padding: 30px;">
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                        Dear <strong>{guardian_name or 'Guardian'}</strong>,
                    </p>
                    
                    <p style="font-size: 16px; color: #333; margin: 0 0 20px 0;">
                        This is to inform you that <strong>{student_name}</strong> has {action} school.
                    </p>
                    
                    <!-- Details Card -->
                    <table width="100%" cellpadding="15" cellspacing="0" style="background-color: #f8f9fa; border-radius: 10px; margin: 20px 0;">
                        <tr>
                            <td style="border-bottom: 1px solid #e9ecef;">
                                <strong style="color: #666;">Student Name:</strong>
                                <span style="float: right; color: #333;">{student_name}</span>
                            </td>
                        </tr>
                        {"<tr><td style='border-bottom: 1px solid #e9ecef;'><strong style='color: #666;'>Year Level:</strong><span style='float: right; color: #333;'>" + year_level + "</span></td></tr>" if year_level else ""}
                        <tr>
                            <td style="border-bottom: 1px solid #e9ecef;">
                                <strong style="color: #666;">Date:</strong>
                                <span style="float: right; color: #333;">{date_str}</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="border-bottom: 1px solid #e9ecef;">
                                <strong style="color: #666;">Time:</strong>
                                <span style="float: right; color: #333; font-weight: bold;">{time_str}</span>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <strong style="color: #666;">Status:</strong>
                                <span style="float: right; color: {action_color}; font-weight: bold;">{status_text}</span>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            
            {image_section}
            
            <!-- Note -->
            <tr>
                <td style="padding: 0 30px 30px 30px;">
                    <p style="font-size: 14px; color: #666; margin: 0;">
                        This is an automated message from the FaceTrack Attendance System.
                    </p>
                </td>
            </tr>
            
            <!-- Footer -->
            <tr>
                <td style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="font-size: 12px; color: #999; margin: 0;">
                        FaceTrack Attendance System<br>
                        Powered by Facial Recognition Technology
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Plain text version
    text_body = f"""
FaceTrack Attendance Notification

Dear {guardian_name or 'Guardian'},

This is to inform you that {student_name} has {action} school.

Details:
- Student: {student_name}
{f"- Year Level: {year_level}" if year_level else ""}
- Date: {date_str}
- Time: {time_str}
- Status: {status_text}

{"A photo of the student was captured and is attached to this email." if image_path else ""}

This is an automated message from the FaceTrack Attendance System.
    """
    
    # Send asynchronously with image
    send_email_async(guardian_email, subject, html_body, text_body, image_path)
    return True


def test_email_config():
    """
    Test the email configuration.
    
    Returns:
        dict: Test result with status and message
    """
    if not SMTP_CONFIG["email"] or not SMTP_CONFIG["password"]:
        return {
            "success": False,
            "message": "Email not configured. Set SMTP_EMAIL and SMTP_PASSWORD."
        }
    
    try:
        with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as server:
            if SMTP_CONFIG["use_tls"]:
                server.starttls()
            server.login(SMTP_CONFIG["email"], SMTP_CONFIG["password"])
        
        return {
            "success": True,
            "message": "Email configuration is valid!"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Email configuration error: {str(e)}"
        }


if __name__ == "__main__":
    # Test email configuration
    print("Testing email configuration...")
    result = test_email_config()
    print(f"Result: {result['message']}")
    
    if result["success"]:
        # Send a test email
        test_email = input("Enter test email address: ").strip()
        if test_email:
            send_attendance_notification(
                guardian_email=test_email,
                guardian_name="Test Guardian",
                student_name="Test Student",
                log_type="IN",
                timestamp=datetime.now(),
                year_level="BSIT - 1st Year",
                image_path=None  # No test image
            )
            print("Test email sent!")
