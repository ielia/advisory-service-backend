from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, false
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.article_tie import ArticleTie
from app.models.feed import Feed
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin
from app.models.mixins.soft_delete import SoftDeleteMixin
from app.models.scored_label import ScoredLabel
from app.models.scored_topic import ScoredTopic
from app.models.tag import Tag


class Article(DefaultValuesMixin, AuditMixin, SerializerMixin, SoftDeleteMixin, db.Model):
    __Plural__ = 'Articles'
    __singular__ = 'article'
    __tablename__ = 'articles'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    feed_id: Mapped[int] = Column(Integer, ForeignKey(Feed.id), nullable=False)
    url: Mapped[str] = Column(String(4000), nullable=False)
    title: Mapped[str] = Column(Text, nullable=False)
    summary: Mapped[str] = Column(Text, nullable=False)
    ai_summary: Mapped[str] = Column(Text)
    full_text: Mapped[str] = Column(Text)
    published: Mapped[datetime] = Column(DateTime, nullable=False)
    following: Mapped[bool] = Column(Boolean, default=False, server_default=false(), nullable=False)
    notes: Mapped[str] = Column(Text)

    __non_deleted_unique_constraints__ = [[url]]

    feed: Mapped[Feed] = relationship(Feed, back_populates='articles')
    original_ties: Mapped[List[ArticleTie]] = relationship(ArticleTie, foreign_keys=[ArticleTie.original_article_id],
                                                           back_populates='original_article', lazy='select')
    followup_ties: Mapped[List[ArticleTie]] = relationship(ArticleTie, foreign_keys=[ArticleTie.followup_article_id],
                                                           back_populates='followup_article', lazy='select')
    scored_topics: Mapped[List[ScoredTopic]] = relationship(ScoredTopic, foreign_keys=[ScoredTopic.article_id],
                                                            back_populates='article', lazy='joined')
    scored_labels: Mapped[List[ScoredLabel]] = relationship(ScoredLabel, foreign_keys=[ScoredLabel.article_id],
                                                            back_populates='article', lazy='joined')
    tags: Mapped[List[Tag]] = relationship(Tag, foreign_keys=[Tag.article_id], back_populates='article', lazy='joined')


ArticleHistory = Article.create_history_model()
