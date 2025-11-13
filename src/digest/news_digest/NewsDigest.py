import json
import os
import random

from openai import OpenAI
from utils import File, Log, Time, TimeUnit

from digest.article import Article
from digest.news_digest.NewsDigestReadMeMixin import NewsDigestReadMeMixin

log = Log("NewsDigest")


class NewsDigest(NewsDigestReadMeMixin):
    MAX_CONTENT_LEN = 1_000_000
    MAX_DAYS_OLD = 7
    MODEL = "gpt-5"

    @staticmethod
    def get_article_in_time_window() -> list[Article]:
        articles = Article.list_all()
        min_time_ut = (
            Time.now().ut - NewsDigest.MAX_DAYS_OLD * TimeUnit.SECONDS_IN.DAY
        )
        articles_in_time_window = [
            a for a in articles if a.time_ut >= min_time_ut
        ]
        log.debug(
            f"Found {len(articles_in_time_window)} articles in time window."
        )
        return articles_in_time_window

    @staticmethod
    def get_news_article_content() -> str:
        articles_in_time_window = NewsDigest.get_article_in_time_window()

        content = ""
        used_articles = []
        total_len = 0
        random.shuffle(articles_in_time_window)
        for article in articles_in_time_window:
            total_len += len(article.all_text) + 3
            used_articles.append(article)
            if total_len > NewsDigest.MAX_CONTENT_LEN:
                break
        content = "\n...\n".join([a.all_text for a in used_articles])
        used_articles.sort(key=lambda a: a.time_ut, reverse=True)
        log.debug(
            f"Selected {len(content):,}B content"
            + f" based on {len(used_articles)} articles random articles"
            + f" from {len(articles_in_time_window)}."
        )
        return content, used_articles

    def __init__(self):
        self.news_article_content, self.used_articles = (
            self.get_news_article_content()
        )
        self.system_prompt = (
            File(os.path.join("prompts", "digest.json.txt")).read().strip()
        )

    def __validate_digest_articles__(self, digest_article_list):
        n_digest_articles = len(digest_article_list)
        assert n_digest_articles > 0, "No items in digest data"
        first_item = digest_article_list[0]
        assert "title" in first_item, "No title in first item"
        assert "body" in first_item, "No body in first item"

    def get_digest_article_list(self):
        log.debug(f"Generating digest with {self.MODEL}...")
        client = OpenAI()
        response = client.responses.create(
            model=self.MODEL,
            reasoning={"effort": "low"},
            input=[
                {
                    "role": "system",
                    "content": self.system_prompt,
                },
                {
                    "role": "user",
                    "content": self.news_article_content,
                },
            ],
        )
        digest_article_list = json.loads(response.output_text)
        self.__validate_digest_articles__(digest_article_list)
        log.info(f"Generated digest with {len(digest_article_list)} items.")
        return digest_article_list

    def build(self):
        self.build_readme()
