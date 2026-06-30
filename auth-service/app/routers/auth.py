from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResendVerificationCodeRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.security import get_current_user
from app.services.auth_service import AuthService
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.services.user_service import UserService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(data)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(data: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.verify_email(data)


@router.post("/resend-verification-code", response_model=MessageResponse)
async def resend_verification_code(data: ResendVerificationCodeRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.resend_verification_code(data)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me/avatar", response_model=UserResponse)
async def update_my_avatar(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    image_url = await upload_image_to_cloudinary(
        file=file,
        folder="avatars",
    )
    service = UserService(db)
    return await service.update_avatar(
        user=current_user,
        image_url=image_url,
    )