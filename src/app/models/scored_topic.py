from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, Text, false
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class ScoredTopic(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
    __Plural__ = 'ScoredTopics'
    __singular__ = 'scored_topic'
    __tablename__ = 'scored_topics'

    article_id: Mapped[int] = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    topic_id: Mapped[int] = Column(Integer, ForeignKey('topics.id'), primary_key=True)
    score: Mapped[float] = Column(Numeric(precision=10, scale=10))
    manually_set: Mapped[bool] = Column(Boolean, default=False, server_default=false(), nullable=False)
    notes: Mapped[str] = Column(Text)

    article: Mapped['Article'] = relationship('Article', back_populates='scored_topics')
    topic: Mapped['Topic'] = relationship('Topic', back_populates='scored_topics')


ScoredTopicHistory = ScoredTopic.create_history_model()
