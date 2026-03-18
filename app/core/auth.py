from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi.security import OAuth2PasswordRequestForm
from jwt import decode, encode

from app.core.security import AccessTokenDep
from app.core.settings import settings
from app.dependencies.services import RefreshSessionServiceDep, UserServiceDep
from app.models.refresh import RefreshSession, RefreshSessionCreate
from app.models.users import UserModel
from app.schemas.auth import AuthTokenData
from app.services.refresh import RefreshSessionService
from app.services.users import UserService
from app.utils.hasher import Hasher


class Authenticator:
    __user_service: UserService
    __refresh_session_service: RefreshSessionService

    def __init__(
        self,
        user_service: UserServiceDep,
        refresh_session_service: RefreshSessionServiceDep,
    ):
        self.__user_service = user_service
        self.__refresh_session_service = refresh_session_service

    async def __generate_tokens(self, user_id: UUID) -> Optional[AuthTokenData]:
        has_active_sessions = (
            await self.__refresh_session_service.has_user_active_session(user_id)
        )

        if has_active_sessions:
            return None

        now = datetime.now(timezone.utc)

        access_token_id = uuid4()
        access_token_lifetime_timedelta = timedelta(
            seconds=settings.auth.access_token_lifetime_seconds
        )
        access_token_expires_at = now + access_token_lifetime_timedelta
        access_token = self.__create_user_token(
            user_id=user_id,
            token_id=access_token_id,
            expires_at=access_token_expires_at,
        )

        refresh_token_id = uuid4()
        refresh_token_lifetime_timedelta = timedelta(
            seconds=settings.auth.refresh_token_lifetime_seconds
        )
        refresh_token_expires_at = now + refresh_token_lifetime_timedelta
        refresh_token = self.__create_user_token(
            user_id=user_id,
            token_id=refresh_token_id,
            expires_at=refresh_token_expires_at,
        )

        session_create_data = RefreshSessionCreate(
            user_id=user_id,
            access_token_id=access_token_id,
            refresh_token_id=refresh_token_id,
            expires_at=refresh_token_expires_at,
        )
        await self.__refresh_session_service.create_session(session_create_data)
        return AuthTokenData(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def __create_user_token(
        self, user_id: UUID, token_id: UUID, expires_at: datetime
    ) -> str:
        payload = {
            'sub': str(user_id),
            'exp': expires_at,
            'jti': str(token_id),
            'iat': datetime.now(timezone.utc),
        }
        return encode(
            payload=payload,
            key=settings.auth.secret.get_secret_value(),
            algorithm=settings.auth.algorithm,
        )

    def __decode_token(self, token: str) -> dict:
        return decode(
            jwt=token,
            key=settings.auth.secret.get_secret_value(),
            algorithms=(settings.auth.algorithm,),
        )

    async def __get_user_token_data(
        self, token: str
    ) -> Optional[tuple[RefreshSession, UUID, UUID]]:
        decoded_payload = self.__decode_token(token)
        raw_user_id = decoded_payload.get('sub', uuid4())

        user_id = UUID(raw_user_id)

        user_active_session = (
            await self.__refresh_session_service.get_active_user_session(user_id)
        )

        if user_active_session is None:
            return None

        raw_token_id = decoded_payload.get('jti', uuid4())
        token_id = UUID(raw_token_id)

        return user_active_session, user_id, token_id

    async def authenticate_user(
        self, access_token: AccessTokenDep
    ) -> Optional[UserModel]:
        token_data = await self.__get_user_token_data(access_token)
        if token_data is None:
            return None
        user_active_session, user_id, access_token_id = token_data

        if user_active_session.access_token_id != access_token_id:
            return None

        return await self.__user_service.get_user(user_id)

    async def create_tokens(
        self, auth_data: OAuth2PasswordRequestForm
    ) -> Optional[AuthTokenData]:
        user = await self.__user_service.get_user_by_username(auth_data.username)
        password = auth_data.password
        if user is None:
            return None
        if not Hasher.verify_password(password, user.password_hash):
            return None
        return await self.__generate_tokens(user.id)

    async def refresh_tokens(self, refresh_token: str) -> Optional[AuthTokenData]:
        token_data = await self.__get_user_token_data(refresh_token)
        if token_data is None:
            return None
        user_active_session, user_id, refresh_token_id = token_data

        if user_active_session.refresh_token_id != refresh_token_id:
            return None

        user_active_session.is_invalidated = True
        await self.__refresh_session_service.save_session(user_active_session)

        return await self.__generate_tokens(user_id)

    async def logout(self, access_token: AccessTokenDep) -> bool:
        token_data = await self.__get_user_token_data(access_token)
        if token_data is None:
            return False
        user_active_session, _, access_token_id = token_data

        if user_active_session.access_token_id != access_token_id:
            return False

        user_active_session.is_invalidated = True
        await self.__refresh_session_service.save_session(user_active_session)

        return True
