from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, Text, false
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class ArticleTie(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
    __Plural__ = 'ArticleTies'
    __singular__ = 'article_tie'
    __tablename__ = 'article_ties'

    original_article_id: Mapped[int] = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    followup_article_id: Mapped[int] = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    similarity: Mapped[float] = Column(Numeric(precision=10, scale=10))
    manually_set: Mapped[bool] = Column(Boolean, default=False, server_default=false(), nullable=False)
    notes: Mapped[str] = Column(Text)

    original_article: Mapped['Article'] = relationship('Article', foreign_keys=[original_article_id],
                                                       back_populates='original_ties', lazy='joined')
    followup_article: Mapped['Article'] = relationship('Article', foreign_keys=[followup_article_id],
                                                       back_populates='followup_ties', lazy='joined')


ArticleTieHistory = ArticleTie.create_history_model()
