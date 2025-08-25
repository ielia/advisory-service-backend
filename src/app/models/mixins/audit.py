from datetime import datetime, timezone
from enum import Enum
from typing import cast, Iterable, TYPE_CHECKING

from flask import g
from sqlalchemy import BinaryExpression, Column, DateTime, Integer, String, Table, Text, and_, event
from sqlalchemy.orm import foreign, relationship
from sqlalchemy.orm.attributes import get_history
from stringcase import snakecase

from app.db import db
from app.models.server_side.sd_utc_now import SDUTCNow
from app.models.mixins.serializer import SerializerMixin


class ChangeType(Enum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3


EVENT_TO_CHANGE_TYPE = {
    'after_insert': ChangeType.CREATE,
    'after_update': ChangeType.UPDATE,
    'after_delete': ChangeType.DELETE
}


class AuditMetaMixin:
    if TYPE_CHECKING:
        class _TableWithColumns(Table):
            columns: Iterable[Column]

        __singular__: str
        __table__: _TableWithColumns
        __tablename__: str


class AuditMixin(AuditMetaMixin):
    @classmethod
    def create_history_model(cls: db.Model) -> type[db.Model]:
        """Create a history table class for this model."""
        if getattr(cls, '__singular__') is None:
            raise f"Class {cls.__name__} needs a member called __singular__ with the singular name of the table."

        copied_columns = {}
        model_id_cols = []
        for col in cls.__table__.columns:
            if col.primary_key:
                model_id_cols.append(col)
                continue
            copied_columns[col.name] = Column(col.type)

        history_cls_name: str = f"{cls.__name__}History"
        history_table_name: str = f"{cls.__tablename__}_history"
        model_id_col_names: list[str] = [c.name for c in model_id_cols]
        ref_id_col_names: list[str] = [f"{snakecase(cls.__singular__)}_{cn}" for cn in model_id_col_names]
        parent_rel_name: str = 'history'
        child_rel_name: str = snakecase(cls.__name__)

        audit_columns = {
            'id': Column(Integer, primary_key=True, autoincrement=True),
            'change_type': Column(String(max(len(ct.name) for ct in ChangeType)), nullable=False),
            'change_date': Column(DateTime, default=lambda: datetime.now(timezone.utc), server_default=SDUTCNow(),
                                  nullable=False),
            'change_user_id': Column(String(100), nullable=False),
            'change_reason': Column(Text),
            **{ref_id_name: Column(id_col.type, nullable=False) for id_col, ref_id_name in
               zip(model_id_cols, ref_id_col_names)},
        }

        history_cls: type[db.Model] = type(
            history_cls_name,
            (SerializerMixin, db.Model),
            {
                '__tablename__': history_table_name,
                **audit_columns,
                **copied_columns
            }
        )

        cast(BinaryExpression, and_(
            *[getattr(cls, id_name) == foreign(getattr(history_cls, ref_id_name)) for id_name, ref_id_name in
              zip(model_id_col_names, ref_id_col_names)]))
        setattr(
            cls,
            'history',
            relationship(
                history_cls,
                primaryjoin=cast(BinaryExpression,
                                 and_(*[
                                     getattr(cls, id_name) == foreign(getattr(history_cls, ref_id_name))
                                     for id_name, ref_id_name in zip(model_id_col_names, ref_id_col_names)
                                 ])),
                back_populates=child_rel_name,
                viewonly=True,
            )
        )
        setattr(
            history_cls,
            snakecase(cls.__name__),
            relationship(
                cls,
                primaryjoin=cast(BinaryExpression,
                                 and_(*[
                                     getattr(cls, id_name) == foreign(getattr(history_cls, ref_id_name))
                                     for id_name, ref_id_name in zip(model_id_col_names, ref_id_col_names)
                                 ])),
                back_populates=parent_rel_name,
                viewonly=True,
            )
        )

        for evt in EVENT_TO_CHANGE_TYPE.keys():
            event.listen(cls, evt,
                         cls._log_history(history_cls, model_id_col_names, ref_id_col_names, EVENT_TO_CHANGE_TYPE[evt]))

        return history_cls

    @staticmethod
    def _log_history(history_cls: type[db.Model], model_id_col_names: list[str], ref_id_col_names: list[str],
                     change_type: ChangeType):
        def log(mapper, connection, target):
            values = {
                c.name: getattr(target, c.name)
                for c in target.__table__.columns
                if not c.primary_key and c.name in history_cls.__table__.columns
            }
            values['change_type'] = (
                ChangeType.DELETE if change_type == ChangeType.UPDATE and
                                     target.deleted and get_history(target, 'deleted').has_changes()
                else change_type).name
            values['change_date'] = datetime.now(timezone.utc)
            values['change_user_id'] = getattr(g, 'audit_user_id', 'N/A')
            values['change_reason'] = getattr(g, 'audit_change_reason', None)
            for id_name, ref_id_name in zip(model_id_col_names, ref_id_col_names):
                values[ref_id_name] = getattr(target, id_name)

            connection.execute(history_cls.__table__.insert().values(**values))

        return log
