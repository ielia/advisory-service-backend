from typing import Any, Iterable, TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy.sql.schema import Column, Table


class SerializerMixin:
    if TYPE_CHECKING:
        class _TableWithColumns(Table):
            columns: Iterable[Column]

        __table__: _TableWithColumns

    def to_dict(self) -> dict[str, Any]:
        return {
            c.name: (lambda value: (value.isoformat() if value else None) if isinstance(c.type, DateTime) else value)(
                getattr(self, c.name)
            )
            for c in self.__table__.columns
        }
