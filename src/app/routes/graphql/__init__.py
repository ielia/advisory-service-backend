# from typing import List
#
# # import strawberry
# # from strawberry.flask.views import GraphQLView
# # from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper
#
# import graphene
# from flask import Blueprint, jsonify, request
# from graphene_sqlalchemy import SQLAlchemyObjectType
# from graphql import graphql_sync
#
# # from app.db import db
# from app.models.article import Article, ArticleHistory
# from app.models.article_tie import ArticleTie, ArticleTieHistory
# from app.models.feed import Feed, FeedHistory
# from app.models.label import Label, LabelHistory
# from app.models.scored_label import ScoredLabel, ScoredLabelHistory
# from app.models.scored_topic import ScoredTopic, ScoredTopicHistory
# from app.models.tag import Tag, TagHistory
# from app.models.topic import Topic, TopicHistory
# from app.models.topic_label import TopicLabel, TopicLabelHistory
# from app.models.user import User, UserHistory
#
# # SQLALCHEMY_MODELS = [Article, ArticleHistory, ArticleTie, ArticleTieHistory, Feed, FeedHistory, Label, LabelHistory,
# #                      ScoredLabel, ScoredLabelHistory, ScoredTopic, ScoredTopicHistory, Tag, TagHistory, Topic,
# #                      TopicHistory, TopicLabel, TopicLabelHistory, User, UserHistory]
#
# # strawberry_sqlalchemy_mapper = StrawberrySQLAlchemyMapper()
#
#
# # @strawberry_sqlalchemy_mapper.type(ArticleHistory)
# class ArticleHistoryType(SQLAlchemyObjectType):
#     # article: 'ArticleType'
#     class Meta:
#         model = ArticleHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(Article)
# class ArticleType(SQLAlchemyObjectType):
#     # feed: 'FeedType'
#     # original_ties: List['ArticleTieType']
#     # followup_ties: List['ArticleTieType']
#     # scored_topics: List['ScoredTopicType']
#     # scored_labels: List['ScoredLabelType']
#     # tags: List['TagType']
#     # history: List[ArticleHistoryType]
#     class Meta:
#         model = Article
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(ArticleTieHistory)
# class ArticleTieHistoryType(SQLAlchemyObjectType):
#     # article_tie: 'ArticleTieType'
#     class Meta:
#         model = ArticleTieHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(ArticleTie)
# class ArticleTieType(SQLAlchemyObjectType):
#     # original_article: ArticleType
#     # followup_article: ArticleType
#     # history: List[ArticleTieHistoryType]
#     class Meta:
#         model = ArticleTie
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(FeedHistory)
# class FeedHistoryType(SQLAlchemyObjectType):
#     # feed: 'FeedType'
#     class Meta:
#         model = FeedHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(Feed)
# class FeedType(SQLAlchemyObjectType):
#     # articles: List[ArticleType]
#     # history: List[FeedHistoryType]
#     class Meta:
#         model = Feed
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(LabelHistory)
# class LabelHistoryType(SQLAlchemyObjectType):
#     # label: 'LabelType'
#     class Meta:
#         model = LabelHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(Label)
# class LabelType(SQLAlchemyObjectType):
#     # scored_labels: List['ScoredLabelType']
#     # topic_labels: List['TopicLabelType']
#     # history: List[LabelHistoryType]
#     class Meta:
#         model = Label
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(ScoredLabelHistory)
# class ScoredLabelHistoryType(SQLAlchemyObjectType):
#     # scored_label: 'ScoredLabelType'
#     class Meta:
#         model = ScoredLabelHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(ScoredLabel)
# class ScoredLabelType(SQLAlchemyObjectType):
#     # article: ArticleType
#     # label: LabelType
#     # history: List[ScoredLabelHistoryType]
#     class Meta:
#         model = ScoredLabel
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(ScoredTopicHistory)
# class ScoredTopicHistoryType(SQLAlchemyObjectType):
#     # scored_topic: 'ScoredTopicType'
#     class Meta:
#         model = ScoredTopicHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(ScoredTopic)
# class ScoredTopicType(SQLAlchemyObjectType):
#     # article: ArticleType
#     # topic: 'TopicType'
#     # history: List[ScoredTopicHistoryType]
#     class Meta:
#         model = ScoredTopic
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(TagHistory)
# class TagHistoryType(SQLAlchemyObjectType):
#     # tag: 'TagType'
#     class Meta:
#         model = TagHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(Tag)
# class TagType(SQLAlchemyObjectType):
#     # article: ArticleType
#     # topic: 'TopicType'
#     # history: List[TagHistoryType]
#     class Meta:
#         model = Tag
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(TopicHistory)
# class TopicHistoryType(SQLAlchemyObjectType):
#     # topic: 'TopicType'
#     class Meta:
#         model = TopicHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(Topic)
# class TopicType(SQLAlchemyObjectType):
#     # scored_topics: List[ScoredTopicType]
#     # tags: List[TagType]
#     # topic_labels: List['TopicLabelType']
#     # history: List[TopicHistoryType]
#     class Meta:
#         model = Topic
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(TopicLabelHistory)
# class TopicLabelHistoryType(SQLAlchemyObjectType):
#     # topic_label: 'TopicLabelType'
#     class Meta:
#         model = TopicLabelHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(TopicLabel)
# class TopicLabelType(SQLAlchemyObjectType):
#     # topic: TopicType
#     # label: LabelType
#     # history: List[TopicLabelHistoryType]
#     class Meta:
#         model = TopicLabel
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(UserHistory)
# class UserHistoryType(SQLAlchemyObjectType):
#     # user: 'UserType'
#     class Meta:
#         model = UserHistory
#         interfaces = (graphene.relay.Node,)
#
#
# # @strawberry_sqlalchemy_mapper.type(User)
# class UserType(SQLAlchemyObjectType):
#     # history: List[UserHistoryType]
#     class Meta:
#         model = User
#         interfaces = (graphene.relay.Node,)
#
#
# # def create_graphql_types_from_models(models: list[type[db.Model]]) -> dict[str, type]:
# #     """Dynamically creates a Strawberry type for each SQLAlchemy model."""
# #
# #     types = {}
# #     for model_cls in models:
# #         type_name = f"{model_cls.__name__}Type"
# #         new_class = type(type_name, (object,), {})
# #         types[type_name] = strawberry_sqlalchemy_mapper.type(model_cls)(new_class)
# #     for model_cls in models:
# #         type_name = f"{model_cls.__name__}Type"
# #         current_type = types[type_name]
# #         relationships = inspect(model_cls).relationships
# #         for relationship_name, rel in relationships.items():
# #             related_type_name = f"{rel.mapper.class_.__name__}Type"
# #             resolver = lambda root: getattr(root, relationship_name)
# #             lazy_type = strawberry.lazy(f"'{related_type_name}'")
# #             field_type = List[lazy_type] if rel.uselist else lazy_type
# #
# #             def create_field_with_type(name: str, resolver_fn, type_hint):
# #                 def resolver_func(self):
# #                     return resolver_fn(self)
# #
# #                 resolver_func.__annotations__['return'] = type_hint
# #                 return strawberry.field(resolver=resolver_func)
# #
# #             field = create_field_with_type(relationship_name, resolver, field_type)
# #             setattr(current_type, relationship_name, field)
# #
# #     return types
# #
# #
# # # Call the function to generate your types
# # graphql_types = create_graphql_types_from_models(SQLALCHEMY_MODELS)
# # ArticleType = graphql_types['ArticleType']
#
#
# # @strawberry.type
# class Query(graphene.ObjectType):
#     # @strawberry.field
#     # def articles(self) -> list[ArticleType]:
#     #     return db.session.query(Article).all()
#     all_articles = graphene.List(ArticleType)
#     all_feeds = graphene.List(FeedType)
#
#     def resolve_all_feeds(root, info):
#         return Feed.query.all()
#
#     def resolve_all_articles(root, info):
#         return Article.query.all()
#
#
# # schema = strawberry.Schema(query=Query)
# # graphql_view = GraphQLView.as_view('graphql_view', schema=schema)
#
# graphql_bp = Blueprint('graphql', __name__, url_prefix='/graphql')
# graphql_schema = graphene.Schema(query=Query)
#
# @graphql_bp.post('/graphql')
# def graphql_server():
#     data = request.get_json()
#     success, result = graphql_sync(graphql_schema, data, context_value=request)
#     return jsonify(result)
