from sqlalchemy import Column, Integer, Numeric
from sqlalchemy.orm import Mapped

from app.db import db


class ScoredLabelTopic(db.Model):
    __Plural__ = 'ScoredLabelTopics'
    __singular__ = 'scored_label_topic'
    __tablename__ = 'view_scored_label_topics'
    __table_args__ = {'info': {'is_view': True, 'skip_autogenerate': True}}

    article_id: Mapped[int] = Column(Integer, primary_key=True)
    label_id: Mapped[int] = Column(Integer, primary_key=True)
    topic_id: Mapped[int] = Column(Integer, primary_key=True)

    topic_label_weight: Mapped[float] = Column(Numeric(precision=10, scale=10))

    @classmethod
    def __view_definition__(cls):
        return """
        SELECT 
            sl.article_id,
            sl.label_id,
            st.topic_id,
            tl.weight AS topic_label_weight
        FROM {ScoredLabel.__tablename__} sl
        JOIN {TopicLabel.__tablename__} tl ON sl.label_id = tl.label_id
        JOIN {ScoredTopic.__tablename__} st ON st.topic_id = tl.topic_id AND st.article_id = sl.article_id
        WHERE tl.enabled = 1
        """
