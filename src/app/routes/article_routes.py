from typing import cast

from flask import Blueprint, Response, current_app, jsonify
from sqlalchemy.orm import joinedload

from app.db import db
from app.models.article import Article, ArticleHistory
from app.models.label import Label
from app.models.tag import Tag
from app.models.topic import Topic
from app.models.topic_label import TopicLabel
from app.routes import set_up_common_routes
from app.typing import FlaskWithServices

app = cast(FlaskWithServices, current_app)

article_bp = Blueprint("articles", __name__, url_prefix="/articles")

set_up_common_routes(
    article_bp,
    Article,
    ArticleHistory,
    "article_id",
    [
        "followup_ties",
        "original_ties",
        "scored_topics.topic.topic_labels.label",
        "tags",
    ],
)


@article_bp.post("/<int:id_value>/follow")
def follow_article(id_value: int) -> tuple[Response, int]:
    article = Article.query.get_or_404(id_value)
    if article.following:
        return jsonify(
            {
                "article": article.to_dict(),
                "result": "ok",
                "message": f"Article {article.id} already being followed",
            }
        ), 200  # or error 409

    with db.session.no_autoflush:
        tags, topics, topic_labels, labels = app.ai_service.add_generated_tags(article)
        # Prefer pre-existing labels over recently generated ones
        new_labels = list(labels)
        preexisting_labels = (
            db.session.query(Label)
            .filter(Label.text.in_([label.text for label in new_labels]))
            .all()
        )
        for p_label in preexisting_labels:
            idx, dup_label = next(
                (
                    label
                    for label in enumerate(new_labels)
                    if label[1].text == p_label.text
                ),
                None,
            )
            del new_labels[idx]
            if db.session.is_active and dup_label in db.session:
                db.session.expunge(dup_label)
            for tl in topic_labels:
                if tl.label is dup_label:
                    tl.label = p_label
                    tl.label_id = p_label.id
        # Save entities
        db.session.add_all(topics)
        db.session.add_all(tags)
        db.session.add_all(new_labels)
        db.session.add_all(topic_labels)
        db.session.add(article)
        db.session.commit()
    return jsonify(
        {
            "article": article.to_dict(),
            "generated_tags": [tag.to_dict() for tag in tags],
            "generated_topics": [topic.to_dict() for topic in topics],
            "generated_labels": [
                {**tl.label.to_dict(), "topic_id": tl.topic_id, "weight": tl.weight}
                for tl in topic_labels
            ],
            "result": "ok",
            "message": f"Article {article.id} now being followed",
        }
    ), 201


@article_bp.delete(
    "/<int:id_value>/follow"
)  # a DELETE does not have a response body, but if we switch to POST it will
def unfollow_article(id_value: int) -> tuple[Response, int]:
    article = Article.query.get_or_404(id_value)
    if not article.following:
        return jsonify(
            {
                "article": article.to_dict(),
                "result": "ok",
                "message": f"Article {article.id} was not being followed",
            }
        ), 204  # or error 409

    tags: list[Tag] = (
        db.session.query(Tag)
        .filter(Tag.article_id == article.id)
        .options(
            joinedload(Tag.topic).joinedload(Topic.tags),
            joinedload(Tag.topic)
            .joinedload(Topic.topic_labels)
            .joinedload(TopicLabel.label)
            .joinedload(Label.topic_labels)
            .joinedload(TopicLabel.topic),
        )
        .all()
    )

    with db.session.no_autoflush:
        article.following = False
        db.session.add(article)

        tags_to_delete: set[Tag] = set(tags)
        topics_to_delete: set[Topic] = set()
        for tag in tags:
            db.session.delete(tag)
            topic: Topic = tag.topic
            if not topic.is_global and (
                len(topic.tags) == 1 or tags_to_delete.issuperset(topic.tags)
            ):
                topics_to_delete.add(topic)
                db.session.delete(topic)
        for topic in topics_to_delete:
            for tl in topic.topic_labels:
                db.session.delete(tl)
                label = tl.label
                if len(label.topic_labels) == 1 or topics_to_delete.issuperset(
                    [tl.topic for tl in label.topic_labels]
                ):
                    db.session.delete(label)

        db.session.commit()

    return jsonify(
        {
            "article": article.to_dict(),
            "result": "ok",
            "message": f"Article {article.id} is not being followed any longer",
        }
    ), 204


@article_bp.post("/<int:id_value>/summarize")
def generate_ai_summary(id_value: int) -> tuple[Response, int]:
    article = Article.query.get_or_404(id_value)
    if article.ai_summary is None:
        app.ai_service.add_generated_summary(article)
        db.session.add(article)
        db.session.commit()
        return jsonify(
            {
                "article": article.to_dict(),
                "result": "ok",
                "message": f"Article {article.id} summarized",
            }
        ), 201
    else:
        return jsonify(
            {
                "article": article.to_dict(),
                "result": "ok",
                "message": f"Article {article.id} already had an AI summary",
            }
        ), 200  # or error 409
