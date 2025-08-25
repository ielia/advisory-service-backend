from flask import Blueprint

from app.models.article import Article, ArticleHistory
from app.routes import set_up_common_routes

article_bp = Blueprint('articles', __name__, url_prefix='/articles')

set_up_common_routes(article_bp, Article, ArticleHistory, 'article_id')
