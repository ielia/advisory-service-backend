from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, true
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin
from app.models.mixins.soft_delete import SoftDeleteMixin


class TopicLabel(DefaultValuesMixin, AuditMixin, SerializerMixin, SoftDeleteMixin, db.Model):
    __Plural__ = 'TopicLabels'
    __singular__ = 'topic_label'
    __tablename__ = 'topic_labels'

    topic_id: Mapped[int] = Column(Integer, ForeignKey('topics.id'), primary_key=True)
    label_id: Mapped[int] = Column(Integer, ForeignKey('labels.id'), primary_key=True)
    weight: Mapped[float] = Column(Numeric(precision=10, scale=10), nullable=False)
    enabled: Mapped[bool] = Column(Boolean, default=True, server_default=true(), nullable=False)

    topic: Mapped['Topic'] = relationship('Topic', back_populates='topic_labels')
    label: Mapped['Label'] = relationship('Label', back_populates='topic_labels')


TopicLabelHistory = TopicLabel.create_history_model()
