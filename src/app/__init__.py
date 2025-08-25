from typing import cast

from flask import Flask, Response, g, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from app.config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.db import db
from app.exceptions.model_validation_error import ModelValidationError
from app.exceptions.request_validation_error import RequestValidationError
from app.routes.article_routes import article_bp
from app.routes.feed_routes import feed_bp
from app.routes.label_routes import label_bp
from app.routes.topic_routes import topic_bp
from app.routes.user_routes import user_bp
from app.services.ai_service import AIService
from app.services.auth_service import AuthService
from app.services.fake_auth_service import FakeAuthService
from app.services.hugging_face_service import HuggingFaceService
from app.services.rss_service import RSSService
from app.typing import FlaskWithServices

migrate = Migrate()


def create_app(config_name: str = 'development') -> FlaskWithServices:
    app = Flask(__name__)
    config_cls = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }[config_name]
    config_obj = config_cls()
    app.config.from_object(config_cls)
    app.json.sort_keys = False

    app.register_blueprint(article_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(label_bp)
    app.register_blueprint(topic_bp)
    app.register_blueprint(user_bp)

    register_error_handlers(app)
    register_audit_context(app)

    db.init_app(app)

    migrate.init_app(app, db)

    app = cast(FlaskWithServices, app)
    app.ai_service = HuggingFaceService(config_obj)
    app.auth_service = FakeAuthService(config_obj)
    app.rss_service = RSSService(config_obj)

    return app


def register_audit_context(app):
    @app.before_request
    def set_audit_context():
        # Example: store current user ID in Flask's 'g'
        # Replace this with your actual user auth logic
        g.audit_user_id = "my-user"  # getattr(g, 'current_user', None) and g.current_user.id or 0

        # Optionally, get a change reason from headers or request JSON
        g.audit_change_reason = request.headers.get("X-Change-Reason", None)


def register_error_handlers(app):
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err: IntegrityError) -> tuple[Response, int]:
        db.session.rollback()
        return jsonify({
            "error": "Database integrity error",
            "message": str(err.orig)
        }), 500

    @app.errorhandler(ModelValidationError)
    def handle_model_validation_error(err: ModelValidationError) -> tuple[Response, int]:
        db.session.rollback()
        return jsonify({
            "result": "error",
            "error": "Model Validation Error",
            "type_structure": err.type_structure,
            "validation_errors": err.validation_errors
        }), 400

    @app.errorhandler(RequestValidationError)
    def handle_model_validation_error(err: RequestValidationError) -> tuple[Response, int]:
        db.session.rollback()
        return jsonify({
            "result": "error",
            "error": "Request Error",
            "message": err.message,
        }), 400
