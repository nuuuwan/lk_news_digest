from digest.article.ArticleBase import ArticleBase
from digest.article.ArticleMetadataMixin import ArticleMetadataMixin
from digest.article.ArticleTextMixin import ArticleTextMixin


class Article(ArticleBase, ArticleTextMixin, ArticleMetadataMixin):
    pass
