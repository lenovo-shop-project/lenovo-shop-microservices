import enum
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from jwt import InvalidTokenError
from pydantic import BaseModel
from app.config import settings


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"


class CurrentUser(BaseModel):
    id: int
    role: UserRole
    email: str | None = None


bearer_scheme = HTTPBearer(
    auto_error=False,
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
) -> CurrentUser:
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
    role = payload.get("role")

    if user_id is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный токен",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        return CurrentUser(
            id=int(user_id),
            role=UserRole(role),
            email=payload.get("email"),
        )
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный токен",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error


def require_role(required_role: UserRole):
    """Разрешает доступ только указанной роли."""

    async def check_role(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )

        return current_user

    return check_role