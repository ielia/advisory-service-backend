from abc import abstractmethod, ABC

from app.models import TopicLabel
from app.models.article import Article
from app.models.label import Label
from app.models.scored_label import ScoredLabel
from app.models.scored_topic import ScoredTopic
from app.models.tag import Tag
from app.models.topic import Topic


class AIService(ABC):
    @abstractmethod
    def add_generated_summary(self, article: Article) -> str:
        pass

    @abstractmethod
    def add_generated_tags(self, article: Article) -> tuple[list[Tag], list[Topic], list[TopicLabel], list[Label]]:
        pass

    @abstractmethod
    def add_topic_scores(self, article: Article) -> tuple[list[ScoredLabel], list[ScoredTopic]]:
        pass
