import json
import os
from pathlib import Path
from typing import Any, Generator

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    CONFIG_FILES = ['config.json', os.environ.get('SECRETS_FILE', 'secrets.json')]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _config: dict[str, Any] = {}

    def __init__(self):
        for filename in self.CONFIG_FILES:
            for data in self.read_json(filename):
                self._config.update(data)

    def get(self, key, default=None):
        return self._config.get(key, default)

    # noinspection PyMethodMayBeStatic
    def read_json(self, filename: str) -> Generator[dict[str, Any], None, None]:
        try:
            if Path(filename).exists():
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    yield data
        except Exception as e:
            print(f"Error opening or reading JSON file: {e}")
            yield {}


class DevelopmentConfig(Config):
    CONFIG_FILES = Config.CONFIG_FILES + ['config.development.json']
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'dev-app-db.sqlite')}"
    )
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"check_same_thread": False}}


class ProductionConfig(Config):
    CONFIG_FILES = Config.CONFIG_FILES + ['config.production.json']
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'prod-app-db.sqlite')}"
    )
    DEBUG = False
