from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, Text, false
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class Tag(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
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

    article_url: Mapped[str] = association_proxy("article", "url")
    article_title: Mapped[str] = association_proxy("article", "title")
    article_summary: Mapped[str] = association_proxy("article", "summary")
    article_ai_summary: Mapped[str] = association_proxy("article", "ai_summary")
    article_full_text: Mapped[str] = association_proxy("article", "full_text")
    article_published: Mapped[datetime] = association_proxy("article", "published")
    article_following: Mapped[bool] = association_proxy("article", "following")
    article_notes: Mapped[str] = association_proxy("article", "notes")
    topic_name: Mapped[str] = association_proxy("topic", "name")
    topic_is_global: Mapped[str] = association_proxy("topic", "is_global")
    topic_enabled: Mapped[bool] = association_proxy("topic", "enabled")
    topic_notes: Mapped[str] = association_proxy("topic", "notes")


TagHistory = Tag.create_history_model()
