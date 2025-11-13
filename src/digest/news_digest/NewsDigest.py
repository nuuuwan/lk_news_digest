import os
import random

from utils import File, Log, Time, TimeUnit

from digest.article import Article
from digest.news_digest.NewsDigestReadMeMixin import NewsDigestReadMeMixin

log = Log("NewsDigest")


class NewsDigest(NewsDigestReadMeMixin):
    DIR_DATA_HISTORY = os.path.join("data", "history")
    MAX_CONTENT_LEN = 1_000_000
    MAX_DAYS_OLD = 7
    MODEL = "gpt-5"
    MODEL_URL = "https://platform.openai.com/docs/models/gpt-5"
    URL_HISTORY = (
        "https://github.com"
        + "/nuuuwan/lk_news_digest"
        + "/tree/main/data/history"
    )

    @staticmethod
    def get_news_article_content() -> str:
        articles = Article.list_all()
        min_time_ut = (
            Time.now().ut - NewsDigest.MAX_DAYS_OLD * TimeUnit.SECONDS_IN.DAY
        )
        articles_in_time_window = [
            a for a in articles if a.time_ut >= min_time_ut
        ]
        content = ""
        used_articles = []
        total_len = 0
        for article in articles_in_time_window:
            total_len += len(article.all_text) + 3
            used_articles.append(article)
            if total_len > NewsDigest.MAX_CONTENT_LEN:
                break
        random.shuffle(used_articles)
        content = "\n...\n".join([a.all_text for a in used_articles])
        used_articles.sort(key=lambda a: a.time_ut, reverse=True)
        return content, used_articles

    def __init__(self):
        self.news_article_content, self.used_articles = (
            self.get_news_article_content()
        )
        self.system_prompt = (
            File(os.path.join("prompts", "digest.txt")).read().strip()
        )
