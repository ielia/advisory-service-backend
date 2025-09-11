import json
import operator
from collections import defaultdict
from collections.abc import Callable
from datetime import date, datetime
from functools import reduce
from typing import Any

from aiodataloader import DataLoader
from ariadne import ObjectType, QueryType, gql, graphql, make_executable_schema
from flask import Blueprint, Response, jsonify, request
from sqlalchemy import Boolean, ColumnElement, Float, Integer, Numeric, and_, case, inspect as sa_inspect, not_, or_, \
    tuple_
from sqlalchemy.ext.associationproxy import AssociationProxyInstance
from sqlalchemy.orm import Session
from sqlalchemy.sql.operators import in_op
from stringcase import snakecase

from app.db import db
from app.models.article import Article, ArticleHistory
from app.models.article_tie import ArticleTie, ArticleTieHistory
from app.models.feed import Feed, FeedHistory
from app.models.label import Label, LabelHistory
from app.models.scored_label import ScoredLabel, ScoredLabelHistory
from app.models.scored_topic import ScoredTopic, ScoredTopicHistory
from app.models.scored_label_topic_view import ScoredLabelTopic
from app.models.tag import Tag, TagHistory
from app.models.topic import Topic, TopicHistory
from app.models.topic_label import TopicLabel, TopicLabelHistory
from app.models.user import User, UserHistory

SUPPORTED_TYPES: dict[type, type] = {
    bool: bool,
    date: date,
    datetime: datetime,
    float: float,
    int: int,
    # default str
}

PYTHON_TYPE_TO_SDL: dict[type, str] = {
    int: 'Int',
    float: 'Float',
    bool: 'Boolean',
    # date: 'String',
    # datetime: 'String',
    # str: 'String',
}

# Dictionary from operator name to (supported_types, list_input, operator_functor) tuple:
FILTER_OPERATORS: dict[str, tuple[set[type], bool, Callable[[object, object], bool]]] = {
    'eq': (set(SUPPORTED_TYPES.keys()), False, operator.eq),
    'ne': (set(SUPPORTED_TYPES.keys()), False, operator.ne),
    'lt': (set(SUPPORTED_TYPES.keys()), False, operator.lt),
    'lte': (set(SUPPORTED_TYPES.keys()), False, operator.le),
    'gt': (set(SUPPORTED_TYPES.keys()), False, operator.gt),
    'gte': (set(SUPPORTED_TYPES.keys()), False, operator.ge),
    'like': (set(SUPPORTED_TYPES.keys()), False, lambda col, val: col.like(val)),
    'ilike': ({str}, False, lambda col, val: col.ilike(val)),
    'startswith': ({str}, False, lambda col, val: col.like('%' + val)),
    'endswith': ({str}, False, lambda col, val: col.like(val + '%')),
    'istartswith': ({str}, False, lambda col, val: col.ilike('%' + val)),
    'iendswith': ({str}, False, lambda col, val: col.ilike(val + '%')),
    'contains': ({str}, False, lambda col, val: col.contains(val)),
    'in': (set(SUPPORTED_TYPES.keys()), True, lambda col, val: col.in_(val)),
}
DEFAULT_FILTER_OPERATOR = FILTER_OPERATORS['eq'][2]

# Dictionary from logical operator name to (list_input, operator_functor) tuple:
LOGICAL_OPERATORS: dict[str, tuple[bool, Callable[[db.Model, Any], ColumnElement[bool]]]] = {
    'AND': (True, lambda model, value: and_(*(build_filter(model, v) for v in value))),
    'NAND': (True, lambda model, value: not_(and_(*(build_filter(model, v) for v in value)))),
    'NOR': (True, lambda model, value: not_(or_(*(build_filter(model, v) for v in value)))),
    'NOT': (False, lambda model, value: not_(build_filter(model, value))),
    'OR': (True, lambda model, value: or_(*(build_filter(model, v) for v in value))),
    'XOR': (True, lambda model, value: reduce(lambda a, b: a + b,
                                              [case((build_filter(model, v), 1), else_=0) for v in value]) == 1),
}


# T = TypeVar('T')
#
# # TODO: Think about moving this function to a different file.
# def get_main_dirname() -> str:
#     flask_app_path = os.environ.get('FLASK_APP')
#     if flask_app_path:
#         if ':' in flask_app_path:
#             # It's a module path (e.g., 'my_app.app:create_app')
#             module_name, _ = flask_app_path.split(':', 1)
#             module = importlib.import_module(module_name)
#             app_absolute_path = Path(module.__file__).resolve()
#         else:
#             app_absolute_path = Path(flask_app_path).resolve()
#         return os.path.dirname(app_absolute_path)
#     else:
#         raise EnvironmentError("FLASK_APP environment variable is not set.")
#
#
# # TODO: Think about moving this function to a different file.
# def get_subclasses(cls: type[T], basedir: str) -> list[type[T]]:
#     """
#     Finds all concrete and abstract subclasses of a given class and returns them in a sorted list, ordered by their
#     class name. This function is robust and finds classes starting from the main filename and all of its submodules.
#
#     Args:
#         cls: The base class to search for subclasses of.
#         basedir: The base directory to test.
#     """
#     all_subclasses = set()
#
#     subclasses = cls.__subclasses__()
#     all_subclasses.update(subclasses)
#     for subclass in subclasses:
#         all_subclasses.update(get_subclasses(subclass, basedir))
#
#     for module in list(sys.modules.values()):
#         try:
#             if hasattr(module, '__file__') and module.__file__ is not None and \
#                     module.__file__.startswith(f"{basedir}{os.sep}"):
#                 for _, obj in inspect.getmembers(module, inspect.isclass):
#                     if issubclass(obj, cls) and obj is not cls:
#                         all_subclasses.add(obj)
#         except (ImportError, AttributeError):
#             continue  # Some modules (e.g., C extensions) may not be introspectable
#
#     return sorted(list(all_subclasses), key=lambda c: c.__name__)
#
#
# # TODO: Think about moving this function to a different file.
# def get_concrete_subclasses(cls: type[T], initial_dir: str) -> list[type[T]]:
#     return [c for c in get_subclasses(cls, initial_dir) if not inspect.isabstract(c)]


def gql_type_from_column(column):
    """Map a SQLAlchemy column to a GraphQL type as SDL string."""
    typ = column.type
    gql_type = 'String'
    if isinstance(typ, Integer):
        gql_type = 'Int'
    elif isinstance(typ, Float) or isinstance(typ, Numeric):
        gql_type = 'Float'
    elif isinstance(typ, Boolean):
        gql_type = 'Boolean'
    # DateTime -> 'String', String -> 'String'
    if not column.nullable:
        gql_type += '!'
    return gql_type


def build_filter(model: db.Model, input_filters: dict) -> ColumnElement[bool]:
    def _and_all(filters) -> ColumnElement[bool]:
        return and_(*filters) if isinstance(filters, list) else filters

    output_filters = []
    for key, value in input_filters.items():
        if key in LOGICAL_OPERATORS:
            output_filters.append(LOGICAL_OPERATORS[key][1](model, value))
        else:
            if '__' in key:
                field_name, op_name = key.split('__', 1)
            else:
                field_name, op_name = key, 'eq'
            column = getattr(model, field_name, None)
            op = FILTER_OPERATORS.get(op_name, None)
            if column and op:
                output_filters.append(op[2](column, value))
            else:
                output_filters.append(DEFAULT_FILTER_OPERATOR(getattr(model, key), value))
    return _and_all(output_filters)


def get_col_values(obj, col_names) -> tuple:
    return tuple(getattr(obj, col_name) for col_name in col_names)


def get_fields(model) -> dict[str, tuple[type, bool, bool]]:
    """ :returns dictionary of field names to (type, collection_flag, nullable_flag) tuple."""
    # TODO: Deal with collections if necessary/possible.
    fields = {}
    inspected_model = sa_inspect(model)
    for column in inspected_model.columns:
        col_type = SUPPORTED_TYPES.get(getattr(column.type, 'python_type', None), str)
        fields[column.key] = (col_type, False, column.nullable)
    for attr_name, attr in [(attr_name, getattr(model, attr_name, None))
                            for attr_name in [n for n in dir(model)
                                              if n not in ('history', 'metadata', 'query', 'query_class', 'registry')
                                                 and n[:1] != '_']]:
        if isinstance(attr, AssociationProxyInstance):
            ass_type = SUPPORTED_TYPES.get(getattr(attr.remote_attr.property.columns[0].type, 'python_type', None), str)
            fields[attr_name] = (ass_type, False, True)  # TODO: Inspect associated model
    return fields


def get_fields_sdl(model) -> list[str]:
    fields = []
    for field_name, (field_type, collection_flag, nullable_flag) in get_fields(model).items():
        gql_type = PYTHON_TYPE_TO_SDL.get(field_type, 'String')
        fields.append(f"{field_name}: {gql_type}{'' if nullable_flag else '!'}")
    return fields


def get_field_filters_sdl(model) -> list[str]:
    fields = []
    for field_name, (field_type, collection_flag, nullable_flag) in get_fields(model).items():
        gql_type = PYTHON_TYPE_TO_SDL.get(field_type, 'String')
        fields.append(f"{field_name}: {gql_type}")  # Default filter: 'eq'
        for op_name, (supported, expects_list, op) in FILTER_OPERATORS.items():
            if field_type in supported:
                input_type = f"[{gql_type}]" if expects_list else gql_type
                fields.append(f"{field_name}__{op_name}: {input_type}")
    return fields


def get_input_filter_sdl(filter_name, model) -> str:
    return (f"input {filter_name} {{\n" + '\n'.join([f"    {line}" for line in get_field_filters_sdl(model)]) +
            '\n    ' +
            '\n    '.join(
                [f"{op_name}: {'[' + filter_name + '!]' if op_list else filter_name}" for op_name, (op_list, op_fn) in
                 LOGICAL_OPERATORS.items()]) +
            '\n}')


def get_pk_col_names(model) -> list[str]:
    return [pk_col.name for pk_col in model.__table__.primary_key]


def get_pk_col_values(obj: db.Model) -> tuple:
    return get_col_values(obj, get_pk_col_names(obj.__class__))


def get_relationships_sdl(model) -> list[str]:
    inspected_model = sa_inspect(model)
    relationships = []
    for rel in inspected_model.relationships.values():
        if rel.uselist:
            relationships.append(
                f"{rel.key}(filter: {rel.mapper.class_.__name__}Filter): [{rel.mapper.class_.__name__}!]!")
        else:
            relationships.append(f"{rel.key}: {rel.mapper.class_.__name__}")
    return relationships


def get_type_sdl(model) -> str:
    return (f"type {model.__name__} {{\n" + '\n'.join([f"    {line}" for line in get_fields_sdl(model)]) + '\n' +
            '\n'.join([f"    {line}" for line in get_relationships_sdl(model)]) + '\n}')


class ChildLoader(DataLoader):
    def __init__(self, session: Session, parent_model: db.Model, child_model: db.Model, rel_name: str, back_rel: str,
                 child_filter: dict, rel_uselist: bool):
        # super().__init__()
        self.session = session
        self.parent_model = parent_model
        self.child_model = child_model
        self.rel_name = rel_name
        self.back_rel = back_rel
        self.child_filter = child_filter
        self.rel_uselist = rel_uselist
        super().__init__(self.batch_load_fn)

    def _build_parents_filter(self, pk_col_names, pk_value_tuples):
        parent_key_values = []
        pk_col_names_tuple = tuple_(*pk_col_names)
        for pk_value_tuple in pk_value_tuples:
            parent_key_values.append(pk_value_tuple)
        return ((pk_col_names_tuple == parent_key_values[0])
                if len(parent_key_values) == 1 else in_op(pk_col_names_tuple,
                                                          parent_key_values) if parent_key_values else None)

    async def batch_load_fn(self, parent_pk_tuples: list[tuple]):
        q = self.session.query(self.child_model)
        if self.child_filter is not None:
            collection_filter = build_filter(self.child_model, self.child_filter)
            if collection_filter is not None:
                q = q.filter(collection_filter)

        parent_pk_col_names = get_pk_col_names(self.parent_model)
        if parent_pk_tuples:
            parents_filter = self._build_parents_filter(parent_pk_col_names, parent_pk_tuples)
            q.filter(parents_filter)

        relationship = self.child_model.__mapper__.relationships[self.back_rel]
        if relationship.secondary is not None:
            q = q.join(relationship.secondary, relationship.primaryjoin).filter(relationship.secondaryjoin)
        q.join(self.parent_model)  # TODO: See if it is possible to avoid getting the parents again.

        children = q.all()

        child_parent_key_values = defaultdict(list)
        for child in children:
            child_parents = getattr(child, self.back_rel)
            if not isinstance(child_parents, list):
                child_parents = [child_parents]
            for child_parent in child_parents:
                child_parent_key_values[get_pk_col_values(child_parent)].append(child)
        results = []
        for parent_kv in parent_pk_tuples:
            result = child_parent_key_values.get(parent_kv, [])
            results.append(result if self.rel_uselist else result[0] if result else None)

        # print(f"Batch function for {self.parent_model.__name__}:{self.rel_name} returning: {len(results)} lists.")
        return results


def create_object_type(model_name: str, model: db.Model, back_rels: dict[str, str] = {}) -> ObjectType:
    """Create ObjectType with relationship resolvers (DataLoader-based)."""
    obj_type = ObjectType(model_name)
    mapper = sa_inspect(model)

    for attr_name in get_fields(model).keys():
        def non_relationship_resolver(parent, info, _attr_name=attr_name):
            return getattr(parent, _attr_name)

        obj_type.set_field(attr_name, non_relationship_resolver)

    for rel in mapper.relationships.values():
        rel_name = rel.key
        rel_uselist = rel.uselist
        child_model = rel.mapper.class_
        back_rel = rel.back_populates
        if back_rel is None:
            back_rel = back_rels[rel_name]

        async def relationship_resolver(parent, info, filter=None, _parent_model=model, _child_model=child_model,
                                        _relationship_name=rel_name, _back_rel=back_rel, _rel_uselist=rel_uselist):
            loaders = info.context.setdefault('loaders', {})
            filter_str = json.dumps(filter, sort_keys=True) if filter else '{}'
            loader_key = f"{_parent_model.__name__}:{_relationship_name}:{filter_str}"
            if loader_key not in loaders:
                loaders[loader_key] = ChildLoader(
                    session=info.context['session'],
                    parent_model=_parent_model,
                    child_model=_child_model,
                    rel_name=_relationship_name,
                    back_rel=_back_rel,
                    child_filter=filter,
                    rel_uselist=_rel_uselist,
                )
            loader = loaders[loader_key]
            return await loader.load(get_pk_col_values(parent))

        obj_type.set_field(rel_name, relationship_resolver)

    return obj_type


def build_schema(models, back_relationships: dict[db.Model, dict[str, str]]):
    type_defs = []
    query_defs = []
    query = QueryType()
    # mutation = MutationType()
    object_types = []

    for model in models:
        model_name = model.__name__
        plural_field = snakecase(model.__Plural__)
        singular_field = model.__singular__
        filter_type_name = f"{model_name}Filter"

        type_defs.append(get_type_sdl(model))
        type_defs.append(get_input_filter_sdl(filter_type_name, model))

        pk_cols = model.__table__.primary_key.columns
        pk_col_names: list[str] = [col.name for col in pk_cols]

        def singular_resolver(obj, info, _model_type: type[db.Model] = model, _pk_columns: list[str] = pk_col_names,
                              **kwargs):
            session = info.context['session']
            pk_values = tuple(kwargs[col] for col in _pk_columns)
            if len(pk_values) == 1:
                pk_values = pk_values[0]
            return session.get(_model_type, pk_values)

        query.field(singular_field)(singular_resolver)
        args_def = ', '.join([f"{col.name}: {gql_type_from_column(col)}" for col in pk_cols])
        query_defs.append(f"{singular_field.lower()}({args_def}): {model_name}")

        def plural_resolver(obj, info, _model_type: type[db.Model] = model, filter: dict = None, **kwargs):
            q = info.context['session'].query(_model_type)
            if filter:
                collection_filter = build_filter(_model_type, filter)
                if collection_filter is not None:
                    q = q.filter(collection_filter)
            return q.all()

        query.field(plural_field)(plural_resolver)
        query_defs.append(f"{plural_field}(filter: {filter_type_name}): [{model_name}!]!")

        object_types.append(create_object_type(model_name, model, back_relationships.get(model, {})))

    type_defs.append(f"type Query {{\n{'\n'.join([f"    {qd}" for qd in query_defs])}\n}}")
    sdl = '\n\n'.join(type_defs)

    # return make_executable_schema(gql("\n".join(type_defs)), query, mutation, *object_types)
    return make_executable_schema(gql(sdl), query, *object_types)


models_to_expose = [Article, ArticleHistory, ArticleTie, ArticleTieHistory, Feed, FeedHistory, Label, LabelHistory,
                    ScoredLabel, ScoredLabelHistory, ScoredLabelTopic, ScoredTopic, ScoredTopicHistory, Tag, TagHistory,
                    Topic, TopicHistory, TopicLabel, TopicLabelHistory, User, UserHistory]
# models_to_expose = get_concrete_subclasses(db.Model, get_main_dirname())

schema = build_schema(models_to_expose, {
    ScoredTopic: {'tags': 'scored_topics'},
    Tag: {'scored_topics': 'tags'},
})

graphql_bp = Blueprint('graphql', __name__, url_prefix='/graphql')


@graphql_bp.post('')
async def graphql_server():
    data = request.get_json()
    success, result = await graphql(schema, data, context_value={'request': request, 'session': db.session}, debug=True)
    status_code = 200 if success else 400
    return jsonify(result), status_code


@graphql_bp.get('/playground')
def graphql_playground():
    # return Response(render_template_string(PLAYGROUND_HTML, settings="{}", share_enabled="false"), mimetype="text/html")
    return Response("""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>GraphiQL</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- GraphiQL CSS -->
    <link rel="stylesheet"
      href="https://unpkg.com/graphiql@1.8.5/graphiql.min.css" />

    <!-- React 17 + ReactDOM 17 (UMD builds) -->
    <script crossorigin src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>

    <!-- GraphiQL (1.x, UMD build) -->
    <script src="https://unpkg.com/graphiql@1.8.5/graphiql.min.js"></script>
  </head>
  <body style="margin:0;overflow:hidden;">
    <div id="graphiql" style="height:100vh;"></div>
    <script>
      const fetcher = graphQLParams =>
        fetch("/graphql", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(graphQLParams),
        }).then(response => response.json());

      ReactDOM.render(
        React.createElement(GraphiQL, { fetcher: fetcher }),
        document.getElementById("graphiql"),
      );
    </script>
  </body>
</html>
""", mimetype='text/html')
