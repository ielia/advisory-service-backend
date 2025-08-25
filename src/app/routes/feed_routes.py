import json
from datetime import timezone
from typing import Generator, cast

from flask import Blueprint, Response, current_app, stream_with_context

from app.db import db
from app.models.article import Article
from app.models.feed import Feed, FeedHistory
from app.routes import set_up_common_routes
from app.typing import FlaskWithServices

feed_bp = Blueprint('feeds', __name__, url_prefix='/feeds')

set_up_common_routes(feed_bp, Feed, FeedHistory, 'feed_id')

app = cast(FlaskWithServices, current_app)


@feed_bp.post('/fetch-all')
def fetch_articles() -> Response:
    total_articles_fetched = 0
    total_articles_processed = 0

    def process_article(feed: Feed, article: Article) -> object:
        ai_service = app.ai_service
        with db.session.no_autoflush:
            scored_labels, scored_topics = ai_service.add_topic_scores(article)
            db.session.add(article)
            db.session.add_all(scored_labels)
            db.session.add_all(scored_topics)
            if feed.last_fetch is None or feed.last_fetch.astimezone(timezone.utc) < article.published.astimezone(timezone.utc):
                feed.last_fetch = article.published
                db.session.add(feed)
            db.session.commit()

        return {
            'article': article.to_dict(),
            'scored_topics': [st.to_dict() for st in scored_topics],
            'scored_labels': [sl.to_dict() for sl in scored_labels],
            'status': 'processed and saved',
        }

    def build_article_response(feed: Feed, article: Article, lbound_datetime) -> tuple[int, str]:
        result: tuple[int, str]
        nonlocal total_articles_fetched
        total_articles_fetched += 1
        if lbound_datetime is None or lbound_datetime.astimezone(timezone.utc) < article.published.astimezone(timezone.utc):
            result = 1, json.dumps(process_article(feed, article))
            nonlocal total_articles_processed
            total_articles_processed += 1
        else:
            result = 0, json.dumps({'article': article.to_dict(), 'status': 'not processed nor saved'})
        return result

    def generate_feed_response(feed: Feed) -> Generator[str]:
        current_call_last_fetch = feed.last_fetch
        yield '{"feed":'
        yield json.dumps(feed.to_dict())
        yield ',\n"articles":[\n'
        articles = app.rss_service.fetch_articles(feed)
        article_process_count = 0
        if len(articles) > 0:
            # noinspection PyTypeChecker
            processed, article_response = build_article_response(feed, articles[0], current_call_last_fetch)
            article_process_count += processed
            yield article_response
            for article in articles[1:]:
                yield ',\n'
                # noinspection PyTypeChecker
                processed, article_response = build_article_response(feed, article, current_call_last_fetch)
                article_process_count += processed
                yield article_response
        yield '\n],"article_fetch_count":' + str(len(articles)) + ',"article_process_count":' + str(article_process_count) + '}'

    def generate_response() -> Generator[str]:
        feeds = Feed.query.all()
        yield '{"feeds":[\n'
        if len(feeds) > 0:
            yield from generate_feed_response(feeds[0])
            for feed in feeds[1:]:
                yield ',\n'
                yield from generate_feed_response(feed)
        nonlocal total_articles_fetched
        nonlocal total_articles_processed
        yield '\n],"result":"ok","message":"' + f"Fetched {total_articles_fetched} article(s) from {len(feeds)} feed(s), of which {total_articles_processed} got processed." + '"}'

    # return Response(stream_with_context(generate_response()), mimetype='application/json', status=202)
    return Response(stream_with_context(generate_response()), mimetype='application/x-ndjson', status=202)
