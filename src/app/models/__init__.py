from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Mapped, foreign, relationship

from app.models.scored_label import ScoredLabel
from app.models.scored_topic import ScoredTopic
from app.models.scored_topic_label_view import ScoredLabelTopic
from app.models.tag import Tag
from app.models.topic_label import TopicLabel

ScoredLabel.scored_topics: Mapped[List[ScoredTopic]] = relationship(
    ScoredTopic,
    secondary=ScoredLabelTopic.__table__,
    primaryjoin=and_(
        ScoredLabel.article_id == ScoredLabelTopic.article_id,
        ScoredLabel.label_id == ScoredLabelTopic.label_id
    ),
    secondaryjoin=and_(
        ScoredLabelTopic.article_id == ScoredTopic.article_id,
        ScoredLabelTopic.topic_id == ScoredTopic.topic_id
    ),
    # back_populates='scored_labels',
    viewonly=True,
    lazy='select'
)

ScoredTopic.scored_labels: Mapped[List[ScoredLabel]] = relationship(
    ScoredLabel,
    secondary=ScoredLabelTopic.__table__,
    primaryjoin=and_(
        ScoredTopic.article_id == ScoredLabelTopic.article_id,
        ScoredTopic.topic_id == ScoredLabelTopic.topic_id
    ),
    secondaryjoin=and_(
        ScoredLabelTopic.article_id == ScoredLabel.article_id,
        ScoredLabelTopic.label_id == ScoredLabel.label_id
    ),
    # back_populates='scored_topics',
    viewonly=True,
    lazy='select'
)

ScoredTopic.tags: Mapped[List[Tag]] = relationship(
    Tag,
    primaryjoin=ScoredTopic.topic_id == foreign(Tag.topic_id),
    # back_populates='scored_topics',
    viewonly=True,
    lazy='select',
)

Tag.scored_topics: Mapped[ScoredTopic] = relationship(
    ScoredTopic,
    primaryjoin=Tag.topic_id == foreign(ScoredTopic.topic_id),
    # back_populates='tags',
    viewonly=True,
    lazy='select',
)
