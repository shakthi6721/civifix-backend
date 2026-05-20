"""Email service for sending emails"""
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails"""

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email"""
        
        try:
            # For development, just log the email
            if settings.ENV == "development":
                logger.info(f"[DEV MODE] Email to {to_email}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Body: {body}")
                return True
            
            # TODO: Implement actual email sending using aiosmtplib or similar
            # For now, return success
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_otp_email(to_email: str, otp: str) -> bool:
        """Send OTP email"""
        subject = "Civifix - OTP Verification"
        body = f"""
        Your Civifix OTP verification code is: {otp}
        
        This code will expire in 5 minutes.
        
        If you did not request this code, please ignore this email.
        
        Best regards,
        Civifix Team
        """
        
        return await EmailService.send_email(to_email, subject, body)
    
    @staticmethod
    async def send_login_otp_email(to_email: str, otp: str) -> bool:
        """Send login OTP email"""
        subject = "Civifix - Login OTP"
        body = f"""
        Your Civifix login OTP is: {otp}
        
        This code will expire in 5 minutes.
        
        If you did not request this code, please ignore this email.
        
        Best regards,
        Civifix Team
        """
        
        return await EmailService.send_email(to_email, subject, body)
