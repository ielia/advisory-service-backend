from flask import Blueprint

from app.models.user import User, UserHistory
from app.routes import set_up_common_routes

user_bp = Blueprint('users', __name__, url_prefix='/users')

set_up_common_routes(user_bp, User, UserHistory, 'user_id')
