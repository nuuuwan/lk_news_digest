import os
import random

from openai import OpenAI
from utils import File, Log, Time, TimeFormat, TimeUnit

from digest.article import Article

log = Log("NewsDigest")


class NewsDigest:
    DIGEST_PATH = "README.md"
    DIR_DATA_HISTORY = os.path.join("data", "history")
    MAX_CONTENT_LEN = 1_000_000
    MAX_DAYS_OLD = 7
    MODEL = "gpt-5"

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

    @property
    def lines_digest(self) -> list[str]:
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
        digest = response.output_text
        log.info(f"Generated digest ({len(digest):,}B).")
        return [digest, "", "---", ""]

    @property
    def lines_used_articles(self) -> list[str]:
        lines = ["## References", ""]
        for i, article in enumerate(self.used_articles, start=1):
            lines.append(
                f"{i}. `{article.date_str}` {article.description}"
                + f" [{article.newspaper_id}]({article.url_metadata})"
            )
        lines.append("")
        return lines

    @property
    def lines_summary(self) -> list[str]:
        time_str = TimeFormat.TIME.format(Time.now())
        n = len(self.used_articles)
        date_strs = [a.date_str for a in self.used_articles]
        min_date_str = min(date_strs)
        max_date_str = max(date_strs)
        return [
            f"Generated at **{time_str}** by **{self.MODEL}**"
            + f" from **{n:,}** English News Articles"
            + f" published between **{min_date_str}** and **{max_date_str}**.",
            "",
        ]

    @property
    def lines_model_details(self) -> list[str]:
        return [
            f"## Model Prompt (for {self.MODEL})",
            "",
            "```",
            self.system_prompt,
            "```",
            "",
        ]

    @property
    def lines(self) -> list[str]:

        return (
            ["# 🇱🇰 Sri Lanka This Week"]
            + self.lines_summary
            + self.lines_digest
            + self.lines_used_articles
            + self.lines_model_details
        )

    def build(self):
        content = "\n".join(self.lines)

        digest_file = File(self.DIGEST_PATH)
        digest_file.write(content)
        log.info(f"Wrote {digest_file}")

        ts = TimeFormat.TIME_ID.format(Time.now())
        os.makedirs(self.DIR_DATA_HISTORY, exist_ok=True)
        history_digest_path = os.path.join(
            self.DIR_DATA_HISTORY, self.DIGEST_PATH[:-3] + f".{ts}.md"
        )
        history_digest_file = File(history_digest_path)
        history_digest_file.write(content)
        log.info(f"Wrote {history_digest_file}")
