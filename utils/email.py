"""
utils/email.py
──────────────
Central email sender for EasePark using the Brevo (Sendinblue) transactional API.

WHY a central utility instead of copy-pasting Brevo code everywhere?
  - api_user_routes.py already had send_otp_email() and send_receipt_email() duplicated.
  - Any change to the email provider (API key format, sender, etc.) used to mean editing
    multiple files. Now there is ONE place to change.
  - Recruiters call this the "DRY principle" (Don't Repeat Yourself).
"""

import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from utils.logger import logger


def _get_brevo_api():
    """Build and return a configured Brevo transactional email API client."""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
    return sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )


def send_email(to_email: str, subject: str, text_content: str) -> bool:
    """
    Generic fire-and-forget email sender.

    Returns True on success, False on failure.
    Errors are intentionally swallowed so a broken email config never crashes
    the main request — callers should log the False return if needed.
    """
    api_instance = _get_brevo_api()
    sender_email = os.getenv("MAIL_DEFAULT_SENDER", "noreply@easepark.com")
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": sender_email, "name": "EasePark"},
        subject=subject,
        text_content=text_content,
    )
    try:
        result = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"[Email] Sent to {to_email} — ID: {result.message_id}")
        return True
    except ApiException as e:
        logger.error(f"[Email] Brevo API error sending to {to_email}: {e.status} - {e.body}")
        return False
    except Exception as e:
        logger.exception(f"[Email] Unexpected error sending to {to_email}: {e}")
        return False


# ── Purpose-specific helpers ────────────────────────────────────────────────────

OTP_EXPIRY_MINUTES = 10


def send_verification_otp(to_email: str, otp: str) -> bool:
    """Send email-address verification OTP during registration."""
    return send_email(
        to_email,
        subject="Verify your EasePark account",
        text_content=(
            f"Hello,\n\n"
            f"Your EasePark email verification OTP is: {otp}\n\n"
            f"This OTP expires in {OTP_EXPIRY_MINUTES} minutes.\n"
            f"Do not share it with anyone.\n\n"
            f"If you did not create an EasePark account, ignore this email."
        ),
    )


def send_password_reset_otp(to_email: str, otp: str) -> bool:
    """Send password-reset OTP triggered by 'Forgot Password'."""
    return send_email(
        to_email,
        subject="Reset your EasePark password",
        text_content=(
            f"Hello,\n\n"
            f"Your EasePark password reset OTP is: {otp}\n\n"
            f"This OTP expires in {OTP_EXPIRY_MINUTES} minutes.\n"
            f"If you did not request a password reset, ignore this email — "
            f"your password has NOT been changed."
        ),
    )


def send_booking_otp(to_email: str, otp: str) -> bool:
    """Send OTP to confirm a parking spot release (existing behaviour, centralised)."""
    return send_email(
        to_email,
        subject="EasePark — Spot Release OTP",
        text_content=(
            f"Your OTP to release your EasePark parking spot is: {otp}\n\n"
            f"This OTP expires in {OTP_EXPIRY_MINUTES} minutes. Do not share it."
        ),
    )
