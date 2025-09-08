from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class ScoredLabel(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
    __Plural__ = 'ScoredLabels'
    __singular__ = 'scored_label'
    __tablename__ = 'scored_labels'

    article_id: Mapped[int] = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    label_id: Mapped[int] = Column(Integer, ForeignKey('labels.id'), primary_key=True)
    score: Mapped[float] = Column(Numeric(precision=10, scale=10), nullable=False)

    article: Mapped['Article'] = relationship('Article', back_populates='scored_labels')
    label: Mapped['Label'] = relationship('Label', back_populates='scored_labels')

    label_text: Mapped[str] = association_proxy("label", "text")
    label_hypothesis: Mapped[str] = association_proxy("label", "hypothesis")


ScoredLabelHistory = ScoredLabel.create_history_model()
