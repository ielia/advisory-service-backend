from flask import Blueprint, Response, jsonify, request

from app.db import db
from app.exceptions.request_validation_error import RequestValidationError
from app.models import TopicLabel
from app.models.label import Label
from app.models.topic import Topic, TopicHistory
from app.routes import set_up_common_routes

topic_bp = Blueprint('topics', __name__, url_prefix='/topics')

set_up_common_routes(topic_bp, Topic, TopicHistory, 'topic_id')

@topic_bp.post('/<int:id_value>/label')
def add_label(id_value: int) -> tuple[Response, int]:
    data = request.get_json()
    hypothesis: str = data.get('hypothesis', None)
    text: str = data.get('text', None)
    weight: int = data.get('weight', None)

    nulls = [p[0] for p in [('hypothesis', hypothesis), ('text', text), ('weight', weight)] if p[1] is None]
    if len(nulls) > 0:
        raise RequestValidationError(f"Missing parameters: {', '.join(nulls)}.")

    topic = Topic.query.get_or_404(id_value)
    label = Label(text=text, hypothesis=hypothesis)
    topic_label = TopicLabel(label=label, topic_id=topic.id, topic=topic, weight=weight, enabled=data.get('enabled', True))
    db.session.add(label)
    db.session.add(topic_label)
    db.session.commit()
    return jsonify({'label': label.to_dict(), 'topic_label': topic_label.to_dict(), 'result': 'ok',
                    'message': f"Label {label.id} created under Topic {topic.id} created"}), 201

@topic_bp.get('/<int:id_value>/labels')
def get_labels(id_value: int) -> tuple[Response, int]:
    topic = Topic.query.get_or_404(id_value)
    return jsonify({'topic': topic.to_dict(),
                    'labels': [{'label': tl.label.to_dict(), 'weight': tl.weight} for tl in topic.topic_labels],
                    'result': 'ok', 'message': f"Topic {topic.id} found"}), 200
