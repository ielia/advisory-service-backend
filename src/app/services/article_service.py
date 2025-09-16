from app.models.article import Article
from app.models.article_tie import ArticleTie
from app.models.scored_topic import ScoredTopic
from app.models.tag import Tag
from app.models.topic import Topic
from app.models.label import Label
from app.models.topic_label import TopicLabel
from app.models.scored_label import ScoredLabel
 
from sqlalchemy import func


class ArticleService():
    
    def __init__(self, config):
        self.tie_score_threshold = config.get('tie-score-threshold')
        
        
    def get_score_for_article(self, article : Article, potential_follow_up : Article):
        
        tags_scores : list[tuple[float,float]] = (Tag.
                                                query.
                                                join(Topic).
                                                join(ScoredTopic).
                                                where(Tag.article == article).
                                                where(ScoredTopic.article == potential_follow_up).
                                                with_entities(Tag.weight, ScoredTopic.score).
                                                tuples().
                                                all()
                                                )
        
        score = sum([weight *  score for (weight, score) in tags_scores])
        
        return score
        
        
    def check_article_followup(self, article : Article, potential_followup : Article) -> tuple[bool, float]:
        
        tags_scores : list[tuple[Tag, ScoredTopic]] = Tag.query.filter(Tag.article_id == article.id).join(ScoredTopic,ScoredTopic.topic_id == Tag.topic_id).all()
        score = sum([ts[0].weight * ts[1].score for ts in tags_scores])

        if score > self.tie_score_threshold:
            return True, score
        
        return False, score
    
    def update_tag_weights(self, article : Article) -> list[Tag]:
        
        topic_labels: list[tuple[TopicLabel,float]] = (
                                                Tag.query.
                                                join(Topic).
                                                join(TopicLabel).
                                                join(Label).
                                                join(ScoredLabel).
                                                where(Tag.article == article).
                                                where(ScoredLabel.article == article).
                                                with_entities(TopicLabel,ScoredLabel.score).
                                                tuples().
                                                all()
            )

        for (topic_label, new_weight) in topic_labels:
            topic_label.weight = new_weight
                
        tag_weights : list[tuple[Tag,float]] = (
                                                Tag.query.
                                                join(Topic).
                                                join(TopicLabel).
                                                where(Tag.article == article).
                                                group_by(Topic.id).
                                                with_entities(Tag, func.avg(TopicLabel.weight)).
                                                tuples().
                                                all()
        )
        
        for (tag, tag_weight) in tag_weights:
            tag.weight = tag_weight
            
        return [tag for (tag, _) in tag_weights]
    
    
    def update_topic_scores(self,article : Article, new_scored_labels : list[ScoredLabel], new_scored_topics : list[ScoredTopic]):
        
        scored_labels : list[ScoredLabel] = ScoredLabel.query.where(ScoredLabel.article == article).all()
        scored_topics : list[ScoredTopic] = ScoredTopic.query.where(ScoredTopic.article == article).all()
        
        for scored_label in scored_labels:
            for new_scored_label in new_scored_labels:
                if new_scored_label.label_id == scored_label.label_id:
                    scored_label.score = new_scored_label.score
    
        for scored_topic in scored_topics:
            for new_scored_topic in new_scored_topics:
                if new_scored_topic.topic_id == scored_topic.topic_id:
                    scored_topic.score = new_scored_topic.score
                    
        return scored_topics, scored_labels
    
    
    def update_followed_article_ties(self, article : Article) -> list[ArticleTie]:
        
        followed_articles = Article.query.where(Article.following).all()
        ties = []
        for followed_article in followed_articles:
            should_tie, score = self.check_article_followup(article, followed_article)
            if should_tie:
                ties.append(ArticleTie(original_article_id = article.id, followup_article_id = followed_article.id, similarity = score))
            
        return ties
        
    
    def update_article_ties(self, article : Article) -> list[ArticleTie]:
        ties = []
            
        articles = Article.query.where(Article.id != article.id).all()
        for art in articles:
            should_tie, score = self.check_article_followup(article, art)
            if should_tie:
                ties.append(ArticleTie(original_article_id = article.id, followup_article_id = art.id, similarity = score))
            
        return ties