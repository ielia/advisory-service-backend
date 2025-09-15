import os
import sys
from datetime import datetime, timezone
from typing import Callable, Generator, TypeVar, cast

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import create_app
from app.db import db
from app.models.article import Article
from app.models.feed import Feed
from app.models.label import Label
from app.models.scored_topic import ScoredTopic
from app.models.scored_label import ScoredLabel
from app.models.tag import Tag
from app.models.topic import Topic

_E = TypeVar('_E')
_R = TypeVar('_R')


@pytest.fixture()
def my_app() -> Generator[Flask]:
    my_app = cast(Flask, create_app('testing'))
    with my_app.app_context():
        db.create_all()
        yield my_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def my_db(my_app: Flask) -> Generator[SQLAlchemy]:
    now_utc = datetime.now(timezone.utc)
    with my_app.app_context():
        f = Feed(id=1, name='Testing Feed', url='https://localhost/f1')
        a1 = Article(id=1, feed_id=1, url='https://localhost/f1/a1', title='TA1', summary='X', published=now_utc)
        a2 = Article(id=2, feed_id=1, url='https://localhost/f1/a2', title='TA2', summary='X', published=now_utc)
        topic1 = Topic(id=1, name='T1')
        topic2 = Topic(id=2, name='T2')
        topic3 = Topic(id=3, name='T3')
        st11 = ScoredTopic(article_id=1, topic_id=1, score=0.5)
        st12 = ScoredTopic(article_id=1, topic_id=2, score=0.6)
        st21 = ScoredTopic(article_id=2, topic_id=1, score=0.7)
        st23 = ScoredTopic(article_id=2, topic_id=3, score=0.8)
        l1 = Label(id=1, text='L1', hypothesis='LH1')
        l2 = Label(id=2, text='L2', hypothesis='LH2')
        l3 = Label(id=3, text='L3', hypothesis='LH3')
        l4 = Label(id=4, text='L4', hypothesis='LH4')
        sl11 = ScoredLabel(article_id=1, label_id=1, score=0.1)
        sl12 = ScoredLabel(article_id=1, label_id=2, score=0.2)
        sl13 = ScoredLabel(article_id=1, label_id=3, score=0.3)
        sl21 = ScoredLabel(article_id=2, label_id=1, score=0.4)
        sl24 = ScoredLabel(article_id=2, label_id=4, score=0.6)
        tag11 = Tag(article_id=1, topic_id=1, weight=1.0)
        tag12 = Tag(article_id=1, topic_id=2, weight=0.9)
        tag23 = Tag(article_id=2, topic_id=3, weight=0.8)
        db.session.add_all([f, a1, a2, topic1, topic2, topic3, st11, st12, st21, st23, l1, l2, l3, l4, sl11, sl12, sl13,
                            sl21, sl24, tag11, tag12, tag23])
        db.session.commit()
        db.session.expunge_all()
        yield db


# def get_article_data() -> Generator[tuple[int, int, int]]:
#     # article_id, num_scored_topics, num_scored_labels
#     tests = [
#         pytest.param(1, 2, 3, id='id=1'),
#         pytest.param(2, 2, 2, id='id=2'),
#     ]
#     for test_data in tests:
#         yield test_data


@pytest.mark.parametrize('article_id, num_scored_topics, num_scored_labels', [
    pytest.param(1, 2, 3, id='id=1'),
    pytest.param(2, 2, 2, id='id=2'),
])
def test_article(my_db: SQLAlchemy, article_id, num_scored_topics, num_scored_labels):
    a = my_db.session.query(Article).get(article_id)
    assert_rel_collection_belongs_to_entity(a.scored_topics, num_scored_topics, lambda x: x.article_id, a.id)
    assert_rel_collection_belongs_to_entity(a.scored_labels, num_scored_labels, lambda x: x.article_id, a.id)


def assert_rel_collection_belongs_to_entity(entity_rel_collection: list, length: int, get_id: Callable[[_E], _R],
                                            id_value: _R):
    assert len(entity_rel_collection) == length
    rel_collection_ids = set(get_id(e) for e in entity_rel_collection)
    assert len(rel_collection_ids) == 1
    assert rel_collection_ids.pop() == id_value
