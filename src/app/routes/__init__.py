from flask import Blueprint, Response, jsonify, request
from flask_sqlalchemy.model import Model
from stringcase import snakecase

from app import db
from app.models.mixins.serializer import SerializerMixin


def set_up_common_routes(bp: Blueprint, cls: type[Model, SerializerMixin], history_cls: type[Model, SerializerMixin], ref_id_field_name: str, expands: list[str] = []):
    @bp.post('/')
    def create() -> tuple[Response, int]:
        data = request.get_json()
        obj = cls(**data)
        db.session.add(obj)
        db.session.commit()
        return jsonify(
            {snakecase(cls.__name__): obj.to_dict(*expands), 'result': 'ok',
             'message': f"{cls.__name__} {obj.id} created"}), 201

    @bp.delete('/<int:id_value>')
    def delete(id_value: int) -> tuple[Response, int]:
        obj = cls.query.get_or_404(id_value)
        db.session.delete(obj)
        db.session.commit()
        return jsonify(
            {snakecase(cls.__name__): obj.to_dict(), 'result': 'ok',
             'message': f"{cls.__name__} {id_value} deleted"}), 200

    @bp.get('/<int:id_value>')
    def get_obj(id_value: int) -> tuple[Response, int]:
        obj = cls.query.get_or_404(id_value)
        return jsonify(
            {snakecase(cls.__name__): obj.to_dict(*expands), 'result': 'ok',
             'message': f"{cls.__name__} id={id_value} found"}), 200

    @bp.get('/<int:id_value>/history')
    def get_history(id_value: int) -> tuple[Response, int]:
        history = history_cls.query.filter(history_cls.get(ref_id_field_name) == id_value).all()
        return jsonify(
            {'history': [item.to_dict() for item in history], 'result': 'ok',
             'message': f"{history_cls.__name__.removesuffix('History')} id={id_value} has {len(history)} change(s)"}), 200

    @bp.get('/')
    def list_objs() -> tuple[Response, int]:
        objs = cls.query.all()
        return jsonify(
            {snakecase(cls.__Plural__): [obj.to_dict(*expands) for obj in objs], 'result': 'ok',
             'message': f"{len(objs)} {cls.__name__} found"}), 200

    @bp.put('/<int:id_value>')
    def update(id_value: int) -> tuple[Response, int]:
        obj = cls.query.get_or_404(id_value)
        data = request.get_json() or {}
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        db.session.commit()
        return jsonify(
            {snakecase(cls.__name__): obj.to_dict(*expands), 'result': 'ok',
             'message': f"{cls.__name__} {obj.id} updated"}), 200
