# import bcrypt
from app.config import Config
from app.services.auth_service import AuthService


class FakeAuthService(AuthService):
    # hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    def __init__(self, config: Config) -> None:
        self.config = config

    def authenticate(self, username: str, password: str) -> str:
        # bcrypt.checkpw(password, stored_hashed_password) --> returns a bool
        return "token"

    def validate_token(self, token: str) -> bool:
        return True
