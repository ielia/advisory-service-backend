# from typing import Generator
#
# from sqlalchemy import Boolean, Column, Index, event, inspect, text
# from sqlalchemy.orm import Session, declarative_mixin, with_loader_criteria
#
# from app.db import db
#
#
# @declarative_mixin
# class SoftDeleteMixin:
#     deleted = Column(Boolean, default=False, server_default=text('0'), nullable=False)
#
#     __non_deleted_unique_constraints__ = []
#
#     def soft_delete(self):
#         self.deleted = True
#
#     @classmethod
#     def set_non_deleted_unique(cls, *cols: list[Column]):
#         """Mark a unique constraint that should only apply when deleted=False"""
#         if not hasattr(cls, '__non_deleted_unique_constraints__'):
#             cls.__non_deleted_unique_constraints__ = []
#         cls.__non_deleted_unique_constraints__.append(cols)
#
#     @classmethod
#     def get_partial_indexes(cls: db.Model, dialect='default'):
#         """Return Index objects for the non-deleted uniques. Handles cross-dialect differences."""
#         indexes = []
#         for columns in getattr(cls, '__non_deleted_unique_constraints__', []):
#             col_names = [c.name for c in columns]
#             name = f"uq_{cls.__tablename__}_{'_'.join(col_names)}_not_deleted"
#             if dialect in {'mariadb', 'mysql'}:  # Unique constraint on (cols..., deleted)
#                 indexes.append(Index(name, *(getattr(cls, c) for c in col_names), cls.deleted, unique=True))
#             elif dialect in {'mssql', 'sqlserver'}:  # Filtered indexes
#                 indexes.append(
#                     Index(name, *(getattr(cls, c) for c in col_names), unique=True, mssql_where=text('deleted=0'))
#                 )
#             elif dialect == 'oracle':  # Function-based index
#                 cond_exprs = [f"{c} * CASE WHEN deleted=0 THEN 1 ELSE NULL END" for c in col_names]
#                 indexes.append(Index(name, *[text(expr) for expr in cond_exprs], unique=True))
#             elif dialect == 'postgresql':  # Native partial unique index
#                 indexes.append(
#                     Index(name, *(getattr(cls, c) for c in col_names), unique=True, postgresql_where=text('NOT deleted'))
#                 )
#             elif dialect == 'sqlite':  # Partial indexes (SQLite v3.8.0+)
#                 indexes.append(
#                     Index(name, *(getattr(cls, c) for c in col_names), unique=True, sqlite_where=text('deleted=0'))
#                 )
#             else:
#                 indexes.append(Index(name, *(getattr(cls, c) for c in col_names), cls.deleted, unique=True))
#         return indexes
#
#
# def _iter_models() -> Generator[type[SoftDeleteMixin]]:
#     for mapper in db.Model.registry.mappers:
#         if issubclass(mapper.class_, SoftDeleteMixin):
#             yield mapper.class_
#
#
# def drop_all_partial_indexes(conn):
#     inspector = inspect(conn)
#     for table in inspector.get_table_names():
#         for ix in inspector.get_indexes(table):
#             ix_name = ix['name']
#             if ix_name.startswith('uq_') and ix_name.endswith('_not_deleted'):
#                 # print(f"Dropping index {ix_name}")
#                 conn.execute(text(f"DROP INDEX {ix['name']}"))
#
#
# # TODO: Fix for downgrades
# def rebuild_partial_indexes(conn):
#     drop_all_partial_indexes(conn)
#     dialect = conn.dialect.name
#     for model in _iter_models():
#         for idx in model.get_partial_indexes(dialect):
#             # print(f"Creating index {idx.name}")
#             idx.create(conn)
#
#
# @event.listens_for(Session, 'before_flush')
# def _soft_delete(session, flush_context, instances):
#     for obj in list(session.deleted):
#         if isinstance(obj, SoftDeleteMixin):
#             obj.soft_delete()
#             session.add(obj)
#             # session._deleted.discard(obj)
#
#
# # noinspection PyTypeChecker
# @event.listens_for(Session, 'do_orm_execute')
# def _filter_deleted(execute_state):
#     if not execute_state.is_column_load and not execute_state.is_relationship_load:
#         if not execute_state.execution_options.get('include_deleted', False):
#             execute_state.statement = execute_state.statement.options(
#                 with_loader_criteria(
#                     SoftDeleteMixin,
#                     lambda cls: cls.deleted == False,
#                     include_aliases=True
#                 )
#             )
