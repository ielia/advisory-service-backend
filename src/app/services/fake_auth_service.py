# import bcrypt

from app.services.auth_service import AuthService


class FakeAuthService(AuthService):
    # hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

    def __init__(self, config):
        pass

    def authenticate(self, username, password) -> str:
        # bcrypt.checkpw(password, stored_hashed_password) --> returns a bool
        return 'token'

    def validate_token(self, token: str) -> bool:
        return True
