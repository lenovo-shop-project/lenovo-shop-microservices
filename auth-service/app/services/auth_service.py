import secrets
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import false, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.email_verification_code import EmailVerificationCode
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    ResendVerificationCodeRequest,
    VerifyEmailRequest,
)
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.services.email_service import send_verification_code_email


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _generate_verification_code(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    async def _create_verification_code(
        self,
        user: User,
    ) -> str:
        old_codes = await self.db.scalars(
            select(EmailVerificationCode).where(
                EmailVerificationCode.user_id == user.id,
                EmailVerificationCode.is_used == false(),
            )
        )

        for old_code in old_codes:
            old_code.is_used = True

        code = self._generate_verification_code()

        verification_code = EmailVerificationCode(
            user_id=user.id,
            code_hash=hash_password(code),
            expires_at=datetime.now(UTC)
            + timedelta(minutes=settings.email_code_expire_minutes),
        )
        self.db.add(verification_code)
        await self.db.commit()
        return code

    async def register(
        self,
        data: RegisterRequest,
    ) -> User:
        email = str(data.email).strip().lower()

        existing_user = await self.db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Користувач із таким email вже існує."
                    "Якщо email не підтверджено, запитайте новий код."
                ),
            )

        first_user_id = await self.db.scalar(
            select(User.id).limit(1)
        )

        if first_user_id is None:
            role = UserRole.ADMIN
        else:
            role = UserRole.CLIENT

        user = User(
            email=email,
            password_hash=hash_password(data.password),
            image_url=data.image_url,
            role=role,
            is_email_verified=False,
        )
        self.db.add(user)

        try:
            await self.db.commit()
            await self.db.refresh(user)

        except IntegrityError as error:
            await self.db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Користувач із таким email вже існує",
            ) from error
        code = await self._create_verification_code(user)
        await send_verification_code_email(
            email=user.email,
            code=code,
        )
        return user

    async def login(
        self,
        data: LoginRequest,
    ) -> dict[str, str]:
        email = str(data.email).strip().lower()

        user = await self.db.scalar(
            select(User).where(User.email == email)
        )

        if user is None or not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний email або пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Підтвердьте email перед входом",
            )
        token = create_access_token(user)
        return {
            "access_token": token,
            "token_type": "bearer",
        }

    async def verify_email(
        self,
        data: VerifyEmailRequest,
    ) -> dict[str, str]:
        email = str(data.email).strip().lower()

        user = await self.db.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Користувач не знайдено",
            )

        if user.is_email_verified:
            return {
                "message": "Email вже підтверджений",
            }

        verification_code = await self.db.scalar(
            select(EmailVerificationCode)
            .where(
                EmailVerificationCode.user_id == user.id,
                EmailVerificationCode.is_used == false(),
                EmailVerificationCode.expires_at > datetime.now(UTC),
            )
            .order_by(
                EmailVerificationCode.created_at.desc(),
            )
        )

        if verification_code is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Код недійсний або прострочений",
            )

        if not verify_password(
            data.code,
            verification_code.code_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний код підтвердження",
            )

        verification_code.is_used = True
        user.is_email_verified = True
        await self.db.commit()
        return {
            "message": "Email успішно підтверджений",
        }

    async def resend_verification_code(
        self,
        data: ResendVerificationCodeRequest,
    ) -> dict[str, str]:
        email = str(data.email).strip().lower()

        user = await self.db.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Користувач не знайдено",
            )

        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email вже підтверджений",
            )
        code = await self._create_verification_code(user)
        await send_verification_code_email(
            email=user.email,
            code=code,
        )
        return {
            "message": "Новий код надіслано на email",
        }