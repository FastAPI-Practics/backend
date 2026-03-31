from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from jwt import decode, encode

from app.core.errors import (
    ForbiddenError,
    InternalServerError,
    LoginError,
    UnauthorizedError,
)
from app.core.security import AccessTokenDep
from app.core.settings import settings
from app.dependencies.services import (
    EmailNotificationServiceDep,
    RefreshSessionServiceDep,
    RoleServiceDep,
    UserServiceDep,
)
from app.models.email import (
    EmailAction,
    EmailNotificationCreate,
    EmailSendData,
    EmailVerificationData,
)
from app.models.refresh import RefreshSession, RefreshSessionCreate
from app.models.users import UserCreate, UserModel, UserStatus
from app.schemas.auth import AuthTokenData, ChangePasswordData
from app.services.refresh import RefreshSessionService
from app.services.roles import RoleService
from app.services.users import UserService
from app.utils.hasher import Hasher


class Authenticator:
    __user_service: UserService
    __refresh_session_service: RefreshSessionService
    __role_service: RoleService
    __email_service: EmailNotificationServiceDep

    def __init__(
        self,
        user_service: UserServiceDep,
        refresh_session_service: RefreshSessionServiceDep,
        role_service: RoleServiceDep,
        email_service: EmailNotificationServiceDep,
    ):
        self.__user_service = user_service
        self.__refresh_session_service = refresh_session_service
        self.__role_service = role_service
        self.__email_service = email_service

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
            raise UnauthorizedError()

        raw_token_id = decoded_payload.get('jti', uuid4())
        token_id = UUID(raw_token_id)

        return user_active_session, user_id, token_id

    async def authenticate_user(
        self, access_token: AccessTokenDep, security_scopes: SecurityScopes
    ) -> Optional[UserModel]:
        token_data = await self.__get_user_token_data(access_token)
        if token_data is None:
            raise UnauthorizedError()
        user_active_session, user_id, access_token_id = token_data

        if user_active_session.access_token_id != access_token_id:
            raise UnauthorizedError()

        user = await self.__user_service.get_user(user_id)

        if user.status != UserStatus.CONFIRMED:
            raise UnauthorizedError()

        if not security_scopes.scopes:
            return user

        user_role = user.role
        user_scopes = user_role.scopes
        for security_scope in security_scopes.scopes:
            if security_scope not in user_scopes:
                raise ForbiddenError()

        return await self.__user_service.get_user(user_id)

    async def login(
        self, auth_data: OAuth2PasswordRequestForm
    ) -> Optional[AuthTokenData]:
        user = await self.__user_service.get_user_by_username(auth_data.username)
        password = auth_data.password
        if user is None:
            raise LoginError()
        if user.status != UserStatus.CONFIRMED:
            raise UnauthorizedError()
        if not Hasher.verify_password(password, user.password_hash):
            raise LoginError()
        return await self.__generate_tokens(user.id)

    async def refresh_tokens(self, refresh_token: str) -> Optional[AuthTokenData]:
        token_data = await self.__get_user_token_data(refresh_token)
        if token_data is None:
            raise UnauthorizedError()
        user_active_session, user_id, refresh_token_id = token_data

        if user_active_session.refresh_token_id != refresh_token_id:
            raise UnauthorizedError()

        user_active_session.is_invalidated = True
        await self.__refresh_session_service.save_session(user_active_session)

        return await self.__generate_tokens(user_id)

    async def logout(self, refresh_token: AccessTokenDep):
        token_data = await self.__get_user_token_data(refresh_token)
        if token_data is None:
            raise UnauthorizedError()
        user_active_session, _, refresh_token = token_data

        if user_active_session.refresh_token_id != refresh_token:
            raise UnauthorizedError()

        user_active_session.is_invalidated = True
        await self.__refresh_session_service.save_session(user_active_session)

    async def register(self, user_create: UserCreate):
        public_role = await self.__role_service.get_by_name(settings.rbac.public_role)
        if public_role is None:
            raise InternalServerError()
        user = await self.__user_service.create_user(user_create)
        user.role = public_role
        await self.__user_service.save_user(user)
        await self.__email_service.send_notification(
            EmailNotificationCreate(user_id=user.id, action=EmailAction.VERIFY_ACCOUNT),
            EmailSendData(
                subject='Account verification',
                email_to=user.email,
                body={
                    'username': user.username,
                    'path': f'/api/v1/auth/user/{user.id}/verify',
                },
                template_name='verification.html',
            ),
        )
        return True

    async def send_password_reset_notification(self, user_id: UUID) -> bool:
        user = await self.__user_service.get_user(user_id)
        if user is None:
            return None
        await self.__email_service.send_notification(
            EmailNotificationCreate(
                user_id=user.id, action=EmailAction.CHANGE_PASSWORD
            ),
            EmailSendData(
                subject='Password reset',
                email_to=user.email,
                body={'username': user.username},
                template_name='password_reset.html',
            ),
        )
        return True

    async def change_password(
        self, user_id: UUID, change_data: ChangePasswordData
    ) -> bool:
        user = await self.__user_service.get_user(user_id)
        if user is None:
            return None
        if user.status != UserStatus.CONFIRMED:
            raise UnauthorizedError()
        if not Hasher.verify_password(
            change_data.old_password.get_secret_value(), user.password_hash
        ):
            raise LoginError()
        notification = await self.__email_service.verify_notification(
            EmailVerificationData(
                user_id=user_id,
                code=change_data.verification_code,
            )
        )
        if notification is None:
            return None
        user.password_hash = Hasher.get_password_hash(
            change_data.new_password.get_secret_value()
        )
        await self.__user_service.save_user(user)
        user_active_session = (
            await self.__refresh_session_service.get_active_user_session(user_id)
        )
        if user_active_session is not None:
            user_active_session.is_invalidated = True
            await self.__refresh_session_service.save_session(user_active_session)
        return True

    async def verify_account(self, user_id: UUID, verification_code: UUID) -> bool:
        notification = await self.__email_service.verify_notification(
            EmailVerificationData(
                user_id=user_id,
                code=verification_code,
            )
        )
        if notification is None:
            return None
        user = await self.__user_service.get_user(user_id)
        if user is None:
            return None
        user.status = UserStatus.CONFIRMED
        await self.__user_service.save_user(user)
        return True
