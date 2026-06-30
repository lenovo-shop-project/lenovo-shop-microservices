from email.message import EmailMessage
import aiosmtplib
from fastapi import HTTPException, status
from app.config import settings


async def send_verification_code_email(
    email: str,
    code: str,
) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP не настроен",
        )

    message = EmailMessage()
    message["From"] = settings.smtp_from or settings.smtp_user
    message["To"] = email
    message["Subject"] = "Код підтвердження email"

    message.set_content(
        f"Ваш код підтвердження: {code}\n\n"
        f"Код дійсний {settings.email_code_expire_minutes} хвилин."
    )

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )