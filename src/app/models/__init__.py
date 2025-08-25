from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Mapped, foreign, relationship

from app.models.scored_label import ScoredLabel
from app.models.scored_topic import ScoredTopic
from app.models.tag import Tag
from app.models.topic_label import TopicLabel

ScoredLabel.scored_topics: Mapped[List[ScoredTopic]] = relationship(
    ScoredTopic,
    secondary=TopicLabel.__table__,
    primaryjoin=ScoredLabel.label_id == foreign(TopicLabel.label_id),
    secondaryjoin=and_(
        TopicLabel.topic_id == foreign(ScoredTopic.topic_id),
        ScoredLabel.article_id == foreign(ScoredTopic.article_id)
    ),
    back_populates='scored_labels',
    viewonly=True,
    lazy='select',
)

ScoredTopic.scored_labels: Mapped[List[ScoredLabel]] = relationship(
    ScoredLabel,
    secondary=TopicLabel.__table__,
    primaryjoin=ScoredTopic.topic_id == foreign(TopicLabel.topic_id),
    secondaryjoin=and_(
        TopicLabel.label_id == foreign(ScoredLabel.label_id),
        ScoredTopic.article_id == foreign(ScoredLabel.article_id)
    ),
    back_populates='scored_topics',
    viewonly=True,
    lazy='select',
)

ScoredTopic.tag: Mapped[Tag] = relationship(
    Tag,
    primaryjoin=and_(ScoredTopic.article_id == foreign(Tag.article_id), ScoredTopic.topic_id == foreign(Tag.topic_id)),
    # back_populates='scored_topic',
    single_parent=True,
    uselist=False,
    viewonly=True,
    lazy='joined',
)

Tag.scored_topic: Mapped[ScoredTopic] = relationship(
    ScoredTopic,
    primaryjoin=and_(Tag.article_id == foreign(ScoredTopic.article_id), Tag.topic_id == foreign(ScoredTopic.topic_id)),
    # back_populates='tag',
    single_parent=True,
    uselist=False,
    viewonly=True,
    lazy='joined',
)
