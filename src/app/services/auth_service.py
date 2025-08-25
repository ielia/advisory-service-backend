from abc import ABC, abstractmethod


# TODO: See to improve this interface.
class AuthService(ABC):
    @abstractmethod
    def authenticate(self, username: str, password: str) -> str:
        pass

    @abstractmethod
    def validate_token(self, token: str) -> bool:
        pass
