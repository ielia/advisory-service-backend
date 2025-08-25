from datetime import timezone
from typing import cast

from flask import Blueprint, Response, current_app, jsonify

from app.db import db
from app.models.feed import Feed, FeedHistory
from app.routes import set_up_common_routes
from app.typing import FlaskWithServices

feed_bp = Blueprint('feeds', __name__, url_prefix='/feeds')

set_up_common_routes(feed_bp, Feed, FeedHistory, 'feed_id')

app = cast(FlaskWithServices, current_app)


@feed_bp.post('/fetch-all')
def fetch_articles() -> tuple[Response, int]:
    feeds = Feed.query.all()
    articles = []
    fetched: int = 0
    for feed in feeds:
        feed_articles = app.rss_service.fetch_articles(feed)
        current_call_last_fetch = feed.last_fetch
        for article in feed_articles:
            if current_call_last_fetch is None or current_call_last_fetch.astimezone(timezone.utc) < article.published:
                scored_labels_and_topics = app.ai_service.add_topic_scores(article)
                scored_labels = scored_labels_and_topics[0]
                scored_topics = scored_labels_and_topics[1]
                if feed.last_fetch is None or feed.last_fetch.astimezone(timezone.utc) < article.published:
                    feed.last_fetch = article.published
                for scored_label in scored_labels:
                    db.session.add(scored_label)
                for scored_topic in scored_topics:
                    db.session.add(scored_topic)
                db.session.add(article)
                db.session.add(feed)
                db.session.commit()
                articles.append({
                    'article': article.to_dict(),
                    'scored_topics': [st.to_dict() for st in scored_topics],
                    'scored_labels': [sl.to_dict() for sl in scored_labels],
                    'status': 'processed and saved',
                })
            else:
                articles.append({'article': article.to_dict(), 'status': 'not processed nor saved'})
            fetched += 1
    return jsonify({'feeds': [f.to_dict() for f in feeds], 'articles': articles, 'result': 'ok',
                    'message': f"Fetched {fetched} articles of which {len(articles)} were processed."}), 200
