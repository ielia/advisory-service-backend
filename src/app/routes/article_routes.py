from typing import cast

from flask import Blueprint, Response, current_app, jsonify

from app.db import db
from app.models.article import Article, ArticleHistory
from app.routes import set_up_common_routes
from app.typing import FlaskWithServices

article_bp = Blueprint('articles', __name__, url_prefix='/articles')

set_up_common_routes(article_bp, Article, ArticleHistory, 'article_id')

app = cast(FlaskWithServices, current_app)


@article_bp.post('/<int:id_value>/summarize')
def generate_ai_summary(id_value: int) -> tuple[Response, int]:
    article = Article.query.get_or_404(id_value)
    app.ai_service.add_generated_summary(article)
    db.session.add(article)
    db.session.commit()
    return jsonify({'article': article.to_dict(), 'result': 'ok', 'message': f"Article {article.id} summarized"}), 200
