from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin
from app.models.mixins.soft_delete import SoftDeleteMixin


class Label(DefaultValuesMixin, AuditMixin, SerializerMixin, SoftDeleteMixin, db.Model):
    __Plural__ = 'Labels'
    __singular__ = 'label'
    __tablename__ = 'labels'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = Column(String(100), nullable=False)
    hypothesis: Mapped[str] = Column(String(100), nullable=False)

    __non_deleted_unique_constraints__ = [[text]]

    scored_labels: Mapped[List['ScoredLabel']] = relationship('ScoredLabel', back_populates='label', lazy='select')
    topic_labels: Mapped[List['TopicLabel']] = relationship('TopicLabel', back_populates='label', lazy='select')


LabelHistory = Label.create_history_model()
