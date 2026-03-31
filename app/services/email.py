from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.settings import settings
from app.dependencies.repositories import (
    EmailNotificationRepository,
    EmailNotificationRepositoryDep,
)
from app.models.email import (
    EmailNotification,
    EmailNotificationCreate,
    EmailSendData,
    EmailVerificationData,
)


class EmailNotificationService:
    __email_notification_repository: EmailNotificationRepository
    __fast_mail: FastMail
    __background_tasks: BackgroundTasks

    def __init__(
        self,
        email_notification_repository: EmailNotificationRepositoryDep,
        background_tasks: BackgroundTasks,
    ):
        self.__email_notification_repository = email_notification_repository
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.email.username,
            MAIL_PASSWORD=settings.email.password,
            MAIL_FROM=settings.email.username,
            MAIL_PORT=settings.email.port,
            MAIL_SERVER=settings.email.server,
            MAIL_FROM_NAME='Vet Clinic App',
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            TEMPLATE_FOLDER='./app/templates',
        )
        self.__background_tasks = background_tasks
        self.__fast_mail = FastMail(conf)

    def send_email(self, email_data: EmailSendData):
        message = MessageSchema(
            subject=email_data.subject,
            recipients=[email_data.email_to],
            template_body=email_data.body,
            subtype='html',
        )
        self.__background_tasks.add_task(
            self.__fast_mail.send_message,
            message,
            template_name=email_data.template_name,
        )

    async def send_notification(
        self, create_data: EmailNotificationCreate, email_data: EmailSendData
    ):
        create_data_dump = create_data.model_dump()
        notification = EmailNotification(**create_data_dump)
        notification.expired_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.email.notification_lifetime_seconds
        )
        notification = await self.__email_notification_repository.save(notification)
        email_data_dump = email_data.model_dump()
        email_data_body = email_data_dump.pop('body')
        body = {
            **email_data_body,
            'code': notification.code,
            'host': settings.common.host,
        }
        self.send_email(EmailSendData(**email_data_dump, body=body))
        return notification

    async def verify_notification(
        self, verification_data: EmailVerificationData
    ) -> Optional[EmailNotification]:
        notifications = await self.__email_notification_repository.fetch(
            verification_data
        )
        if len(notifications) != 1:
            return None
        notification = notifications[0]
        if notification.is_used:
            return None
        notification.is_used = True
        return await self.__email_notification_repository.save(notification)
