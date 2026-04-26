import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.email import EmailAction, EmailNotification
from app.models.users import UserModel


@pytest.mark.asyncio
async def test_auth(async_client: AsyncClient, async_db: AsyncSession):
    register_resp = await async_client.post(
        url='/auth/register',
        json={
            'username': 'test',
            'password': 'qwerty',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'email': 'email@email.com',
        },
    )
    assert register_resp.status_code == status.HTTP_200_OK

    user_select_stmt = select(UserModel).where(UserModel.username == 'test')
    user_data = (await async_db.scalars(user_select_stmt)).first()
    user = UserModel.model_validate(user_data)
    user_id = user.id

    notification_select_stmt = select(EmailNotification).where(
        EmailNotification.user_id == user_id,
        EmailNotification.action == EmailAction.VERIFY_ACCOUNT,
    )
    notification = (await async_db.scalars(notification_select_stmt)).first()

    assert notification is not None

    code = notification.code

    verify_resp = await async_client.get(
        url=f'/auth/user/{user_id}/verify',
        params={
            'code': code,
        },
    )
    assert verify_resp.status_code == status.HTTP_200_OK

    login_resp = await async_client.post(
        url='/auth/login', data={'username': 'test', 'password': 'qwerty'}
    )

    assert login_resp.status_code == status.HTTP_200_OK

    cookies = login_resp.cookies

    login_data = login_resp.json()
    assert 'access_token' in login_data

    refresh_token = cookies.get('refresh_token')

    assert refresh_token is not None

    logout_resp = await async_client.delete(
        url='/auth/logout', cookies={'refresh_token': refresh_token}
    )

    assert logout_resp.status_code == status.HTTP_200_OK

    user = await async_db.get(UserModel, user_id)
    await async_db.delete(user)
    await async_db.commit()

    await async_db.delete(notification)
    await async_db.commit()
