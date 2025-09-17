from flask import Blueprint, Response, jsonify, request

from app.db import db
from app.exceptions.request_validation_error import RequestValidationError
from app.models.label import Label, LabelHistory
from app.models.topic import Topic
from app.models.topic_label import TopicLabel
from app.routes import set_up_common_routes

label_bp = Blueprint("labels", __name__, url_prefix="/labels")

set_up_common_routes(label_bp, Label, LabelHistory, "label_id")


@label_bp.post("/<int:id_value>/topic/<int:topic_id>")
def add_to_topic(id_value: int, topic_id: int) -> tuple[Response, int]:
    data = request.get_json()
    if not hasattr(data, "weight"):
        raise RequestValidationError("Missing weight.")
    weight = data.get("weight")
    label = Label.query.get_or_404(id_value)
    topic = Topic.query.get_or_404(topic_id)
    topic_label = TopicLabel(
        label_id=label.id,
        label=label,
        topic_id=topic.id,
        topic=topic,
        weight=weight,
        enabled=data.get("enabled", True),
    )
    db.session.add(topic_label)
    db.session.commit()
    return jsonify(
        {
            "topic_label": topic_label.to_dict(),
            "result": "ok",
            "message": f"TopicLabel {topic_label.id} created",
        }
    ), 201
