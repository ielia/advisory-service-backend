from flask import Blueprint, Response, abort, jsonify, request
from sqlalchemy.orm import joinedload

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
    topic_label = TopicLabel(label=label, topic_id=topic.id, topic=topic, weight=weight,
                             enabled=data.get('enabled', True))
    db.session.add(label)
    db.session.add(topic_label)
    db.session.commit()
    return jsonify({'label': label.to_dict(), 'topic_label': topic_label.to_dict(), 'result': 'ok',
                    'message': f"Label {label.id} created under Topic {topic.id} created"}), 201


@topic_bp.put('/<int:id_value>/global')
def promote_to_global(id_value: int) -> tuple[Response, int]:
    topic = Topic.query.get_or_404(id_value)
    if topic.is_global:
        return jsonify(
            {'topic': topic.to_dict(), 'result': 'ok', 'message': f"Topic {topic.id} is already global"}), 200
    else:
        topic.is_global = True
        db.session.add(topic)
        db.session.commit()
        return jsonify({'topic': topic.to_dict(), 'result': 'ok', 'message': f"Topic {topic.id} is now global"}), 201


@topic_bp.delete('/<int:id_value>/global')
def demote_from_global(id_value: int) -> tuple[Response, int]:
    topic = Topic.query.get_or_404(id_value)
    if topic.is_global:
        topic.is_global = False
        db.session.add(topic)
        db.session.commit()
        return jsonify(
            {'topic': topic.to_dict(), 'result': 'ok', 'message': f"Topic {topic.id} is no longer global"}), 204
    else:
        return jsonify({'topic': topic.to_dict(), 'result': 'ok', 'message': f"Topic {topic.id} was not global"}), 200


@topic_bp.get('/<int:id_value>/labels')
def get_labels(id_value: int) -> tuple[Response, int]:
    topic = Topic.query.get_or_404(id_value)
    return jsonify({'topic': topic.to_dict(),
                    'labels': [{'label': tl.label.to_dict(), 'weight': tl.weight} for tl in topic.topic_labels],
                    'result': 'ok', 'message': f"Topic {topic.id} found"}), 200


@topic_bp.delete('/<int:id_value>/label/<int:label_id>')
def remove_label(id_value: int, label_id: int) -> tuple[Response, int]:
    topic = Topic.query.options(
        joinedload(Topic.topic_labels).joinedload(TopicLabel.labels).joinedload(Label.topic_labels)
    ).filter(Label.id == label_id).get_or_404(id_value)

    topic_label = next((tl for tl in topic.topic_labels if tl.label.id == label_id), None)

    if topic_label is None:
        abort(404, description=f"Label {label_id} not found under Topic {id_value}")

    label = topic_label.label
    db.session.delete(topic_label)
    if len(label.topic_labels) == 1:
        db.session.delete(label)
        message = f"Label {label_id} was deleted"
    else:
        message = f"Label {label_id} was detached from Topic {topic.id}, but it is still attached to topics {[tl.topic_id for tl in label.topic_labels]}"
    db.session.commit()

    return jsonify({'label': label.to_dict(), 'topic_label': topic_label.to_dict(), 'result': 'ok',
                    'message': message}), 201
