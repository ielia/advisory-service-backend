from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, Boolean, Text, true
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class Topic(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
    __Plural__ = "Topics"
    __singular__ = "topic"
    __tablename__ = "topics"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    is_global: Mapped[bool] = Column(
        Boolean, default=True, server_default=true(), nullable=False
    )
    enabled: Mapped[bool] = Column(
        Boolean, default=True, server_default=true(), nullable=False
    )
    notes: Mapped[str] = Column(Text)

    if TYPE_CHECKING:
        from app.models.scored_topic import ScoredTopic
        from app.models.tag import Tag
        from app.models.topic_label import TopicLabel

        scored_topics: Mapped[List[ScoredTopic]]
        tags: Mapped[List[Tag]]
        topic_labels: Mapped[List[TopicLabel]]

    scored_topics = relationship(
        "ScoredTopic",
        back_populates="topic",
        cascade="all,delete-orphan",
        lazy="select",
    )
    tags = relationship(
        "Tag", back_populates="topic", cascade="all,delete-orphan", lazy="select"
    )
    topic_labels = relationship(
        "TopicLabel", back_populates="topic", cascade="all,delete-orphan", lazy="select"
    )


TopicHistory = Topic.create_history_model()
