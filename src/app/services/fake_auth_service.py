# import bcrypt
from app.services.auth_service import AuthService
from app.config import Config


class FakeAuthService(AuthService):
    # hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    def __init__(self, config: 'Config') -> None:
        pass

    def authenticate(self, username: str, password: str) -> str:
        # bcrypt.checkpw(password, stored_hashed_password) --> returns a bool
        return 'token'

    def validate_token(self, token: str) -> bool:
        return True
