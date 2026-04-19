from pwdlib import PasswordHash


class Hasher:
    __password_hash = PasswordHash.recommended()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Hasher.__password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return Hasher.__password_hash.hash(password)
