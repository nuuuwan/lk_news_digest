from digest.ArticleBase import ArticleBase
from digest.ArticleMetadataMixin import ArticleMetadataMixin
from digest.ArticleTextMixin import ArticleTextMixin


class Article(ArticleBase, ArticleTextMixin, ArticleMetadataMixin):
    pass
