import os
from functools import cached_property

from utils import WWW, File


class ArticleTextMixin:
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
        return os.path.join("data", f"article-{self.doc_id}.txt")

    @cached_property
    def text(self) -> str:
        text_file = File(self.text_path)
        if not text_file.exists:
            os.makedirs("data", exist_ok=True)
            www = WWW(self.text_url)
            content = www.read()
            text_file.write(content)
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
