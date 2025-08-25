from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, Text, and_, false
from sqlalchemy.orm import Mapped, foreign, relationship

from app.db import db
from app.models import ScoredTopic
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin
from app.models.mixins.soft_delete import SoftDeleteMixin


class Tag(DefaultValuesMixin, AuditMixin, SerializerMixin, SoftDeleteMixin, db.Model):
    """This entity represents a relation between an article and a generated topic that was created to follow said article."""

    __Plural__ = 'Tags'
    __singular__ = 'tag'
    __tablename__ = 'tags'

    article_id: Mapped[int] = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    topic_id: Mapped[int] = Column(Integer, ForeignKey('topics.id'), primary_key=True)
    weight: Mapped[float] = Column(Numeric(precision=10, scale=10), default=1.0, server_default=db.text('1.0'))
    manually_set: Mapped[bool] = Column(Boolean, default=False, server_default=false(), nullable=False)
    notes: Mapped[str] = Column(Text)

    article: Mapped['Article'] = relationship('Article', back_populates='tags')
    topic: Mapped['Topic'] = relationship('Topic', back_populates='tags')


TagHistory = Tag.create_history_model()
