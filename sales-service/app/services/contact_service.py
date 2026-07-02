from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contact_message import ContactMessage
from app.models.phone_request import PhoneRequest
from app.schemas.contact import ContactMessageCreate, PhoneRequestCreate
from app.security import CurrentUser


class ContactService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _get_user_email_or_401(
            self,
            current_user: CurrentUser,
    ) -> str:
        if not current_user.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="В токене отсутствует email. Войдите в аккаунт заново",
            )
        return current_user.email

    async def create_contact_message(
        self,
        data: ContactMessageCreate,
        current_user: CurrentUser,
    ) -> ContactMessage:
        contact_message = ContactMessage(
            user_id=current_user.id,
            email=self._get_user_email_or_401(current_user),
            message=data.message.strip(),
        )
        self.db.add(contact_message)
        await self.db.commit()
        await self.db.refresh(contact_message)
        return contact_message

    async def create_phone_request(
        self,
        data: PhoneRequestCreate,
        current_user: CurrentUser,
    ) -> PhoneRequest:
        phone_request = PhoneRequest(
            user_id=current_user.id,
            email=self._get_user_email_or_401(current_user),
            phone_number=data.phone_number.strip(),
        )
        self.db.add(phone_request)
        await self.db.commit()
        await self.db.refresh(phone_request)
        return phone_request

    async def get_all_contact_messages_admin(
        self,
    ) -> list[ContactMessage]:
        result = await self.db.scalars(
            select(ContactMessage)
            .order_by(
                ContactMessage.created_at.desc(),
            )
        )
        return list(result.all())

    async def get_all_phone_requests_admin(
        self,
    ) -> list[PhoneRequest]:
        result = await self.db.scalars(
            select(PhoneRequest)
            .order_by(
                PhoneRequest.created_at.desc(),
            )
        )
        return list(result.all())