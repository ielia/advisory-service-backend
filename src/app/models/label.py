from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.db import db
from app.models.mixins.audit import AuditMixin
from app.models.mixins.default_values import DefaultValuesMixin
from app.models.mixins.serializer import SerializerMixin


class Label(DefaultValuesMixin, AuditMixin, SerializerMixin, db.Model):
    __Plural__ = "Labels"
    __singular__ = "label"
    __tablename__ = "labels"

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = Column(String(100), unique=True, nullable=False)
    hypothesis: Mapped[str] = Column(String(100), nullable=False)

    if TYPE_CHECKING:
        from app.models.scored_label import ScoredLabel
        from app.models.topic_label import TopicLabel

        scored_labels: Mapped[List[ScoredLabel]]
        topic_labels: Mapped[List[TopicLabel]]

    scored_labels = relationship(
        "ScoredLabel",
        back_populates="label",
        cascade="all,delete-orphan",
        lazy="select",
    )
    topic_labels = relationship(
        "TopicLabel", back_populates="label", cascade="all,delete-orphan", lazy="select"
    )


LabelHistory = Label.create_history_model()
