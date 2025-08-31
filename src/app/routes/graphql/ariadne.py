from ariadne import ObjectType, QueryType, gql, graphql_sync, make_executable_schema
from flask import Blueprint, Response, jsonify, request
from sqlalchemy import Boolean, Float, Integer, Numeric, inspect

from app.db import db
from app.models.article import Article, ArticleHistory
from app.models.article_tie import ArticleTie, ArticleTieHistory
from app.models.feed import Feed, FeedHistory
from app.models.label import Label, LabelHistory
from app.models.scored_label import ScoredLabel, ScoredLabelHistory
from app.models.scored_topic import ScoredTopic, ScoredTopicHistory
from app.models.tag import Tag, TagHistory
from app.models.topic import Topic, TopicHistory
from app.models.topic_label import TopicLabel, TopicLabelHistory
from app.models.user import User, UserHistory

PYTHON_TYPE_TO_SDL: dict[type, str] = {
    int: 'Int',
    float: 'Float',
    bool: 'Boolean',
    # date: 'String',
    # datetime: 'String',
    # str: 'String',
}


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


def build_schema(models):
    type_defs = []
    query = QueryType()
    # mutation = MutationType()
    object_types = []
    query_type_created = False

    for model in models:
        model_name = model.__name__
        inspected_model = inspect(model)

        sdl_lines = [f"type {model_name} {{"]
        for column in inspected_model.columns:
            col_type = 'String'
            if hasattr(column.type, 'python_type'):
                col_type = PYTHON_TYPE_TO_SDL.get(column.type.python_type, 'String')
            sdl_lines.append(f"    {column.key}: {col_type}")
        for rel in inspected_model.relationships.values():
            sdl_lines.append(
                f"    {rel.key}: {'[' if rel.uselist else ''}{rel.mapper.class_.__name__}!{']!' if rel.uselist else ''}")
        sdl_lines.append('}')
        type_defs.append('\n'.join(sdl_lines))

        # Query resolvers
        plural_field = model.__Plural__.lower()
        query.field(plural_field)(lambda obj, info, model=model: info.context['session'].query(model).all())

        # Singular with PK args
        pk_cols = model.__table__.primary_key.columns
        pk_col_names: list[str] = [col.name for col in pk_cols]
        args_def = ', '.join([f"{col.name}: {gql_type_from_column(col)}" for col in pk_cols])
        type_defs.append(f"""
{'extend ' if query_type_created else ''}type Query {{
    {plural_field}: [{model_name}!]!
    {model_name.lower()}({args_def}): {model_name}
}}
        """)
        query_type_created = True

        def singular_resolver(obj, info, model_type: type[db.Model] = model, pk_columns: list[str] = pk_col_names,
                              **kwargs):
            session = info.context["session"]
            pk_values = tuple(kwargs[col] for col in pk_columns)
            if len(pk_values) == 1:
                pk_values = pk_values[0]
            return session.get(model_type, pk_values)

        query.field(model_name.lower())(singular_resolver)

        # Object type resolvers
        obj_type = ObjectType(model_name)
        for rel in inspected_model.relationships.values():
            obj_type.field(rel.key)(lambda obj, info, relname=rel.key: getattr(obj, relname))
        object_types.append(obj_type)

    # return make_executable_schema(gql("\n".join(type_defs)), query, mutation, *object_types)
    return make_executable_schema(gql("\n".join(type_defs)), query)


models_to_expose = [Article, ArticleHistory, ArticleTie, ArticleTieHistory, Feed, FeedHistory, Label, LabelHistory,
                    ScoredLabel, ScoredLabelHistory, ScoredTopic, ScoredTopicHistory, Tag, TagHistory, Topic,
                    TopicHistory, TopicLabel, TopicLabelHistory, User, UserHistory]

schema = build_schema(models_to_expose)

graphql_bp = Blueprint('graphql', __name__, url_prefix='/graphql')


@graphql_bp.post('/')
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value={'equest': request, 'session': db.session}, debug=True)
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
