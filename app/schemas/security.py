from pydantic import BaseModel, EmailStr


class AuthData(BaseModel):
    email: EmailStr
    password: str

class RefreshData(BaseModel):
    refresh_token: str

class TokenData(RefreshData):
    access_token: str
    token_type: str = 'Bearer'
