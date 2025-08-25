from typing import Any, Iterable, TYPE_CHECKING

from sqlalchemy.sql.sqltypes import DateTime, DECIMAL, Float, Numeric
from sqlalchemy.sql.schema import Column, Table


class SerializerMixin:
    if TYPE_CHECKING:
        class _TableWithColumns(Table):
            columns: Iterable[Column]

        __table__: _TableWithColumns

    def to_dict(self) -> dict[str, Any]:
        def normalize_value(c_type, value: Any):
            if isinstance(c_type, DateTime):
                return value.isoformat() if value else None
            elif isinstance(c_type, DECIMAL) or isinstance(c_type, Float) or isinstance(c_type, Numeric):
                return float(value)
            elif isinstance(value, SerializerMixin):
                return value.to_dict()
            else:
                return value

        return {c.name: normalize_value(c.type, getattr(self, c.name)) for c in self.__table__.columns}
