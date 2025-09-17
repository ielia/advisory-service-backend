from typing import Any, Iterable, TYPE_CHECKING
from collections import defaultdict

from sqlalchemy import Integer, Boolean
from sqlalchemy.orm import class_mapper, RelationshipProperty
from sqlalchemy.sql.sqltypes import DateTime, DECIMAL, Float, Numeric
from sqlalchemy.sql.schema import Column, Table


class SerializerMixin:
    if TYPE_CHECKING:

        class _TableWithColumns(Table):
            columns: Iterable[Column]

        __table__: _TableWithColumns

    def to_dict(self, *expand: str) -> dict[str, Any]:
        def _build_rel_expand_tree_node(*expand: str) -> dict[str, list[str | None]]:
            expand_split: list[list[str]] = [
                e.split(".", 1) for e in sorted(set(expand)) if e is not None
            ]
            tree_node: dict[str, list[str | None]] = defaultdict(list)
            for path in expand_split:
                tree_node[path[0]].append(path[1] if len(path) > 1 else None)
            return tree_node

        def _normalize_value(
            c_type, val: Any, *exp: str
        ) -> bool | float | int | str | list | dict | None:
            # TODO: Find a better implementation
            if val is None:
                return None
            elif isinstance(val, SerializerMixin):
                return val.to_dict(*exp)
            elif isinstance(val, list):
                return [_normalize_value(c_type, v, *exp) for v in val]
            elif isinstance(c_type, Integer) or isinstance(c_type, Boolean):
                return val
            elif (
                isinstance(c_type, DECIMAL)
                or isinstance(c_type, Float)
                or isinstance(c_type, Numeric)
            ):
                return float(val)
            elif isinstance(c_type, DateTime):
                return val.isoformat() if val else None
            else:
                return str(val)

        data = {
            c.name: _normalize_value(c.type, getattr(self, c.name))
            for c in self.__table__.columns
        }

        if expand:
            expand_dict = _build_rel_expand_tree_node(*expand)
            mapper = class_mapper(self.__class__)
            for rel_name in expand_dict.keys():
                rel_prop: RelationshipProperty = mapper.relationships.get(
                    rel_name, None
                )
                if rel_prop is None:
                    continue  # skip invalid relation names
                value = getattr(self, rel_name)
                data[rel_name] = _normalize_value(
                    rel_prop.argument, value, *expand_dict[rel_name]
                )

        return data
