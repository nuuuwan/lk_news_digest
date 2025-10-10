from dataclasses import dataclass


@dataclass
class ArticleBase:
    newspaper_id: str
    doc_id: str
    date_str: str
    description: str
    lang: str
    url_metadata: str
    time_ut: int

    @property
    def year(self) -> str:
        return self.date_str.split("-")[0]

    @property
    def decade(self) -> str:
        return self.year[:3] + "0s"
