from sqlalchemy import Boolean, Column, Integer, String, true
from sqlalchemy.orm import Mapped

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class User(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
    __Plural__ = 'Users'
    __singular__ = 'user'
    __tablename__ = 'users'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    guid: Mapped[str] = Column(String(100), unique=True, nullable=False)
    username: Mapped[str] = Column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = Column(String(100), nullable=False)
    enabled: Mapped[bool] = Column(Boolean, default=True, server_default=true(), nullable=False)


UserHistory = User.create_history_model()
