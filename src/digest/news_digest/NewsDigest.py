import json
import os
import random

from openai import OpenAI
from utils import File, JSONFile, Log, Time, TimeFormat, TimeUnit

from digest.article import Article
from digest.news_digest.NewsDigestReadMeMixin import NewsDigestReadMeMixin

log = Log("NewsDigest")


class NewsDigest(NewsDigestReadMeMixin):
    MAX_CONTENT_LEN = 1_000_000
    MAX_DAYS_OLD = 7
    MODEL = "gpt-5"
    DIR_DIGESTS = os.path.join("data", "digests")

    @staticmethod
    def __get_article_in_time_window__() -> list[Article]:
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
    def __get_news_article_content__() -> str:
        articles_in_time_window = NewsDigest.__get_article_in_time_window__()

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

    @staticmethod
    def __get_system_prompt__() -> str:
        return File(os.path.join("prompts", "digest.json.txt")).read().strip()

    @staticmethod
    def __validate_digest_articles__(digest_article_list):
        n_digest_articles = len(digest_article_list)
        assert n_digest_articles > 0, "No items in digest data"
        first_item = digest_article_list[0]
        assert "title" in first_item, "No title in first item"
        assert "body" in first_item, "No body in first item"

    @staticmethod
    def __get_digest_article_list__(
        system_prompt, news_article_content, ts
    ) -> list[dict]:
        log.debug(f"Generating digest with MODEL={NewsDigest.MODEL}...")
        client = OpenAI()
        response = client.responses.create(
            model=NewsDigest.MODEL,
            reasoning={"effort": "low"},
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": news_article_content,
                },
            ],
        )
        digest_article_list = json.loads(response.output_text)
        NewsDigest.__validate_digest_articles__(digest_article_list)
        log.info(f"Generated digest with {len(digest_article_list)} items.")

        os.makedirs(NewsDigest.DIR_DIGESTS, exist_ok=True)
        digest_path = os.path.join(NewsDigest.DIR_DIGESTS, f"digest.{ts}.json")
        digest_file = JSONFile(digest_path)
        digest_file.write(digest_article_list)
        log.info(f"Wrote {digest_file}")

        return digest_article_list

    def build(self):
        news_article_content, used_articles = (
            self.__get_news_article_content__()
        )
        system_prompt = self.__get_system_prompt__()
        ts = TimeFormat.TIME_ID.format(Time.now())
        digest_article_list = self.__get_digest_article_list__(
            system_prompt, news_article_content, ts
        )

        self.build_readme(
            used_articles, system_prompt, ts, digest_article_list
        )
