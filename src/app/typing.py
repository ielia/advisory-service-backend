from typing import Protocol

from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.rss_service import RSSService


class FlaskWithServices(Protocol):
    ai_service: AIService
    auth_service: AuthService
    rss_service: RSSService
