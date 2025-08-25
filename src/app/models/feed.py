from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, true
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin
from app.models.mixins.soft_delete import SoftDeleteMixin


class Feed(DefaultValuesMixin, AuditMixin, SerializerMixin, SoftDeleteMixin, db.Model):
    __Plural__ = 'Feeds'
    __singular__ = 'feed'
    __tablename__ = 'feeds'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    url: Mapped[str] = Column(String(4000), nullable=False)
    last_fetch: Mapped[datetime] = Column(DateTime)
    enabled: Mapped[bool] = Column(Boolean, default=True, server_default=true(), nullable=False)
    notes: Mapped[str] = Column(Text)

    __non_deleted_unique_constraints__ = [[name], [url]]

    articles: Mapped[List['Article']] = relationship('Article', back_populates='feed', lazy='select')


FeedHistory = Feed.create_history_model()
