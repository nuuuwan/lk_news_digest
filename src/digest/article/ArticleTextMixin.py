import os
from functools import cached_property

from utils import WWW, File, Log

log = Log("ArticleTextMixin")


class ArticleTextMixin:
    DIR_DATA_ARTICLES = os.path.join("data", "articles")

    @property
    def text_url(self) -> str:
        return (
            "https://raw.githubusercontent.com"
            + "/nuuuwan/lk_news"
            + "/refs/heads/data"
            + f"/data/lk_news/{self.decade}/{self.year}"
            + f"/{self.doc_id}"
            + "/doc.txt"
        )

    @property
    def text_path(self) -> str:
        return os.path.join(
            self.DIR_DATA_ARTICLES, f"article-{self.doc_id}.txt"
        )

    @cached_property
    def text(self) -> str:
        text_file = File(self.text_path)
        if not text_file.exists:
            os.makedirs(self.DIR_DATA_ARTICLES, exist_ok=True)
            www = WWW(self.text_url)
            content = www.read()
            text_file.write(content)
            log.info(f"Wrote {text_file}")
        else:
            content = text_file.read()
        return content

    @cached_property
    def all_text(self):
        return "\n".join(
            [
                "# " + self.description,
                "",
                "Source: " + self.url_metadata,
                "",
                "Date: " + self.date_str,
                "",
                self.text,
            ]
        )
