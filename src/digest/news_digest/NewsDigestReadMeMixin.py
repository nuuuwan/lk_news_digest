import os

from utils import File, Format, Log, Time, TimeFormat

log = Log("NewsDigest")


class NewsDigestReadMeMixin:
    DIR_DATA_README_HISTORY = os.path.join("data", "readme_history")
    DIGEST_PATH = "README.md"
    MODEL_URL = "https://platform.openai.com/docs/models/gpt-5"
    URL_HISTORY = (
        "https://github.com"
        + "/nuuuwan/lk_news_digest"
        + "/tree/main/data/readme_history"
    )

    def get_lines_header(self, used_articles) -> list[str]:
        time_updated = TimeFormat.TIME.format(Time.now())
        time_updated_for_badge = Format.badge(time_updated)

        return [
            self.get_title(),
            "",
            "![LastUpdated](https://img.shields.io/badge"
            + f"/last_updated-{time_updated_for_badge}-green)",
            "[![RSS](https://img.shields.io/badge/RSS-Feed-orange)]"
            + f"({self.RSS_FEED_URL})",
            "",
            self.get_description(used_articles),
            "",
        ]

    def get_lines_digest(self, digest_article_list) -> list[str]:
        log.debug(f"Digest has {len(digest_article_list)} articles.")

        lines = []
        for i_article, digest_article in enumerate(
            digest_article_list, start=1
        ):
            title = digest_article["title"]
            body = digest_article["body"]
            lines.extend(
                [
                    f"## {i_article}. {title}",
                    "",
                    body,
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
                f"[Previous Editions]({self.URL_HISTORY})",
                "",
            ]
        )
        return lines

    def get_lines_used_articles(self, used_articles) -> list[str]:
        lines = ["## References", ""]
        for i, article in enumerate(used_articles, start=1):
            lines.append(
                f"{i}. `{article.date_str}` {article.description}"
                + f" [{article.newspaper_id}]({article.url_metadata})"
            )
        lines.append("")
        return lines

    def get_lines_model_details(self, system_prompt) -> list[str]:
        return [
            f"## Model Prompt (for [{self.MODEL}]({self.MODEL_URL}))",
            "",
            "```",
            system_prompt,
            "```",
            "",
        ]

    def get_lines_footer(self) -> list[str]:
        return [
            "![Maintainer]"
            + "(https://img.shields.io/badge/maintainer-nuuuwan-red)",
            "![MadeWith](https://img.shields.io/badge/made_with-python-blue)",
            "[![License: MIT]"
            + "(https://img.shields.io/badge/License-MIT-yellow.svg)]"
            + "(https://opensource.org/licenses/MIT)",
            "",
        ]

    def get_lines(
        self, used_articles, system_prompt, digest_article_list
    ) -> list[str]:
        return (
            self.get_lines_header(used_articles)
            + self.get_lines_digest(digest_article_list)
            + self.get_lines_used_articles(used_articles)
            + self.get_lines_model_details(system_prompt)
            + self.get_lines_footer()
        )

    @staticmethod
    def get_history_path(ts: str) -> str:
        return os.path.join(
            NewsDigestReadMeMixin.DIR_DATA_README_HISTORY,
            NewsDigestReadMeMixin.DIGEST_PATH[:-3] + f".{ts}.md",
        )

    @staticmethod
    def get_history_url(ts: str) -> str:
        return (
            "https://github.com/nuuuwan/lk_news_digest/blob/main/"
            + NewsDigestReadMeMixin.get_history_path(ts)
        )

    def __save_copy_to_history__(self, content: str, ts: str):
        os.makedirs(self.DIR_DATA_README_HISTORY, exist_ok=True)
        history_digest_path = self.get_history_path(ts)
        history_digest_file = File(history_digest_path)
        history_digest_file.write(content)
        log.info(f"Wrote {history_digest_file}")

    def build_readme(
        self, used_articles, system_prompt, ts, digest_article_list
    ):
        content = "\n".join(
            self.get_lines(used_articles, system_prompt, digest_article_list)
        )
        digest_file = File(self.DIGEST_PATH)
        digest_file.write(content)
        log.info(f"Wrote {digest_file}")

        self.__save_copy_to_history__(content, ts)
