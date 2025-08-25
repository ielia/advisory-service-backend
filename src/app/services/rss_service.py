import sys
from datetime import datetime, timezone

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_datetime

from app.models.article import Article
from app.models.feed import Feed


class RSSService:
    def __init__(self, config):
        pass

    def fetch_articles(self, feed: Feed) -> list[Article]:
        articles: list[Article] = []
        parsed = feedparser.parse(feed.url, modified=feed.last_fetch)
        if not hasattr(parsed, 'status') or parsed.status < 200 or 300 <= parsed.status:
            print(parsed, file=sys.stderr)  # TODO: Deal with error
        else:
            for entry in parsed.entries:
                try:
                    published = self._parse_published_date(entry)
                    if feed.last_fetch is None or published > feed.last_fetch:
                        url = self._get_url(entry)
                        articles.append(Article(
                            feed_id=feed.id,
                            url=url,
                            title=entry.get('title'),
                            summary=entry.get('summary'),
                            full_text=self._get_full_text(url),
                            published=published,
                        ))
                except Exception as e:
                    print(e, file=sys.stderr)  # TODO: Deal with error
        return sorted(articles,
                      key=lambda article: article.published if article.published is not None else datetime.max)

    # noinspection PyMethodMayBeStatic
    def _get_full_text(self, url):
        full_text = None
        try:
            http_response = requests.get(url)
            full_text = BeautifulSoup(http_response.content, 'html.parser').get_text()
        except Exception as e:
            print(e, file=sys.stderr)  # TODO: Deal with error
        return full_text

    # noinspection PyMethodMayBeStatic
    def _get_url(self, entry) -> str:
        return entry.get('link') or entry.get('id')

    # noinspection PyMethodMayBeStatic
    def _parse_published_date(self, entry) -> datetime:
        date_string = entry.get('updated') or entry.get('published')
        date_struct = entry.get('updated_parsed') or entry.get('published_parsed')
        parsed = None
        if date_struct:
            parsed = datetime(*date_struct[:6], tzinfo=timezone.utc)
        elif date_string:
            parsed = parse_datetime(date_string).astimezone(timezone.utc)
        return parsed
