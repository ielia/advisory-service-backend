from typing import cast

from flask import Blueprint, Response, current_app, jsonify
from sqlalchemy.sql.operators import in_op

from app.db import db
from app.models.article import Article, ArticleHistory
from app.models.label import Label
from app.routes import set_up_common_routes
from app.typing import FlaskWithServices

article_bp = Blueprint('articles', __name__, url_prefix='/articles')

set_up_common_routes(article_bp, Article, ArticleHistory, 'article_id')

app = cast(FlaskWithServices, current_app)


@article_bp.post('/<int:id_value>/follow')
def follow_article(id_value: int) -> tuple[Response, int]:
    with db.session.no_autoflush:
        article = Article.query.get_or_404(id_value)
        tags, topics, topic_labels, labels = app.ai_service.add_generated_tags(article)

        # Prefer pre-existing labels over recently generated ones
        preexisting_labels = db.session.query(Label).filter(Label.text.in_([l.text for l in labels])).all()
        for p_label in preexisting_labels:
            label: tuple[int, Label] = next((l for l in enumerate(labels) if l[1].text == p_label.text), None)
            del labels[label[0]]
            for tl in topic_labels:
                if tl.label == label[1]:
                    tl.label = p_label
                    tl.label_id = p_label.id

        db.session.add_all(topics)
        db.session.add_all(tags)
        db.session.add_all(labels)
        db.session.add_all(topic_labels)
        db.session.add(article)
        db.session.commit()

    return jsonify({'article': article.to_dict(), 'generated_tags': [tag.to_dict() for tag in tags],
                    'generated_labels': [{**tl.label.to_dict(), 'topic_id': tl.topic_id, 'weight': tl.weight}
                                         for tl in topic_labels],
                    'result': 'ok', 'message': f"Article {article.id} now being followed"}), 200


@article_bp.post('/<int:id_value>/summarize')
def generate_ai_summary(id_value: int) -> tuple[Response, int]:
    article = Article.query.get_or_404(id_value)
    app.ai_service.add_generated_summary(article)
    db.session.add(article)
    db.session.commit()
    return jsonify({'article': article.to_dict(), 'result': 'ok', 'message': f"Article {article.id} summarized"}), 200
