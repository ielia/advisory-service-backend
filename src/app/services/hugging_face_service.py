import json
import sys
from collections import defaultdict
from decimal import Decimal

import requests

from app.db import db
from app.models.article import Article
from app.models.label import Label
from app.models.scored_label import ScoredLabel
from app.models.scored_topic import ScoredTopic
from app.models.tag import Tag
from app.models.topic import Topic
from app.models.topic_label import TopicLabel
from app.services.ai_service import AIService


class HuggingFaceService(AIService):
    headers: dict[str, str]
    classification_url: str
    labelling_url: str
    summarization_url: str

    def __init__(self, config):
        self.headers = {'Authorization': f"Bearer {config.get('huggingface.access-token')}"}
        base_url = config.get('huggingface.base-url')
        base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.classification_url = f"{base_url}/{config.get('huggingface.classifier-model')}"
        self.labelling_url = f"{base_url}/{config.get('huggingface.labelling-model')}"
        self.summarization_url = f"{base_url}/{config.get('huggingface.summarization-model')}"

    def add_generated_summary(self, article: Article) -> str:
        pass

    def add_generated_tags(self, article: Article) -> list[Tag]:
        pass

    def add_topic_scores(self, article: Article) -> tuple[list[ScoredLabel], list[ScoredTopic]]:
        labels: list[Label] = list(db.session.query(Label).join(TopicLabel).join(Topic).
                                   filter(TopicLabel.enabled == True).filter(Topic.enabled == True).distinct().all())
        labels_by_strs: dict[str, dict[str, Label]] = defaultdict(dict)
        scored_labels_by_ids: dict[int, dict[int, ScoredLabel]] = defaultdict(dict)
        topic_labels_by_ids: dict[int, dict[int, TopicLabel]] = defaultdict(dict)
        # scored_topics: dict[int, ScoredTopic] = {}
        topic_scales: dict[int, Decimal] = defaultdict(Decimal)
        all_scored_labels: list[ScoredLabel] = []
        all_scored_topics: list[ScoredTopic] = []
        for label in labels:
            labels_by_strs[label.hypothesis][label.text] = label
        for hypothesis, labels_by_text in labels_by_strs.items():
            payload = {
                'inputs': article.summary,
                'parameters': {
                    'candidate_labels': list(labels_by_text.keys()),
                    'multi_label': True,
                    'hypothesis_template': hypothesis
                }
            }
            response = requests.post(self.classification_url, headers=self.headers, json=payload)
            self._log_response(self.classification_url, payload, response)
            response.raise_for_status()
            for label_text, label_score in zip(response.json()['labels'], response.json()['scores']):
                label: Label = labels_by_text.get(label_text)
                label_id = label.id
                scored_label = ScoredLabel(article=article, article_id=article.id, label=label, label_id=label_id,
                                           score=Decimal(label_score))
                all_scored_labels.append(scored_label)
                for topic_label in label.topic_labels:
                    topic_id: int = topic_label.topic_id
                    scored_labels_by_ids[topic_id][label_id] = scored_label
                    topic_labels_by_ids[topic_id][label_id] = topic_label
                    topic_scales[topic_id] += Decimal(topic_label.weight)
            for topic_id, scored_labels in scored_labels_by_ids.items():
                topic_score: Decimal = Decimal('0.0')
                topic_scale = topic_scales[topic_id]
                topic_scale = Decimal(1.0) if topic_scale.is_zero() else topic_scale
                for label_id, scored_label in scored_labels.items():
                    topic_label = topic_labels_by_ids[topic_id][label_id]
                    topic_score += Decimal(scored_label.score) * Decimal(topic_label.weight)
                scored_topic = ScoredTopic(article=article, article_id=article.id, topic_id=topic_id,
                                           score=topic_score / topic_scale)
                # scored_topics[topic_id] = scored_topic
                all_scored_topics.append(scored_topic)
        article.scored_topics = all_scored_topics
        return all_scored_labels, all_scored_topics

    # noinspection PyMethodMayBeStatic
    def _log_response(self, url, payload, response) -> None:
        # file = sys.stdout
        # print(f"url: {url}\npayload:\n", file=file)
        # json.dump(payload, file, indent=2)
        # print(f"\nstatus: {response.status_code}\ncontent:\n{response.content}", file=file)
        # print(f"{'-' * 80}", file=file)
        pass
