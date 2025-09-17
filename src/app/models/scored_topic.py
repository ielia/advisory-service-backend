from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, Text, false
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class ScoredTopic(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
    __Plural__ = "ScoredTopics"
    __singular__ = "scored_topic"
    __tablename__ = "scored_topics"

    article_id: Mapped[int] = Column(
        Integer, ForeignKey("articles.id"), primary_key=True
    )
    topic_id: Mapped[int] = Column(Integer, ForeignKey("topics.id"), primary_key=True)
    score: Mapped[float] = Column(Numeric(precision=10, scale=10))
    manually_set: Mapped[bool] = Column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    notes: Mapped[str] = Column(Text)

    if TYPE_CHECKING:
        from app.models.article import Article
        from app.models.topic import Topic

        article: Mapped[Article]
        topic: Mapped[Topic]

    article = relationship("Article", back_populates="scored_topics")
    topic = relationship("Topic", back_populates="scored_topics")

    topic_name: Mapped[str] = association_proxy("topic", "name")
    topic_is_global: Mapped[str] = association_proxy("topic", "is_global")
    topic_enabled: Mapped[bool] = association_proxy("topic", "enabled")
    topic_notes: Mapped[str] = association_proxy("topic", "notes")


ScoredTopicHistory = ScoredTopic.create_history_model()
