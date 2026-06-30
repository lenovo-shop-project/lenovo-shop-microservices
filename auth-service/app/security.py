from datetime import UTC, datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole


password_hash = PasswordHash.recommended()

bearer_scheme = HTTPBearer(
    auto_error=False,
)


def hash_password(password: str) -> str:
    """Хеширует пароль перед сохранением в БД."""

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Проверяет введённый пароль."""

    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user: User) -> str:
    """Создаёт JWT-токен пользователя."""

    now = datetime.now(UTC)

    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.access_token_expire_minutes,
        ),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """Проверяет подпись JWT и возвращает данные токена."""

    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Получает пользователя по Bearer-токену."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    payload = decode_access_token(
        credentials.credentials
    )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="В токене отсутствует идентификатор пользователя",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный токен",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error

    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user


def require_role(required_role: UserRole):
    """Разрешает доступ только указанной роли."""

    async def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )

        return current_user

    return check_role