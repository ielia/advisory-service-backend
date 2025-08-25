from typing import List

from sqlalchemy import Column, Integer, String, Boolean, Text, true
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin
from app.models.mixins.soft_delete import SoftDeleteMixin


class Topic(DefaultValuesMixin, AuditMixin, SerializerMixin, SoftDeleteMixin, db.Model):
    __Plural__ = 'Topics'
    __singular__ = 'topic'
    __tablename__ = 'topics'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    is_global: Mapped[bool] = Column(Boolean, default=True, server_default=true(), nullable=False)
    enabled: Mapped[bool] = Column(Boolean, default=True, server_default=true(), nullable=False)
    notes: Mapped[str] = Column(Text)

    __non_deleted_unique_constraints__ = [[name]]

    scored_topics: Mapped[List['ScoredTopic']] = relationship('ScoredTopic', back_populates='topic', lazy='select')
    tags: Mapped[List['Tag']] = relationship('Tag', back_populates='topic', lazy='select')
    topic_labels: Mapped[List['TopicLabel']] = relationship('TopicLabel', back_populates='topic', lazy='select')


TopicHistory = Topic.create_history_model()
