import os

from utils import WWW, File, TSVFile


class ArticleMetadataMixin:
    LOCAL_METADATA_PATH = os.path.join("data", "docs_last10000.tsv")
    URL_METADATA = (
        "https://raw.githubusercontent.com"
        + "/nuuuwan/lk_news"
        + "/refs/heads/data/data/lk_news/docs_last10000.tsv"
    )

    @classmethod
    def from_dict(cls, d):
        return cls(
            newspaper_id=d["newspaper_id"],
            doc_id=d["doc_id"],
            date_str=d["date_str"],
            description=d["description"],
            lang=d["lang"],
            url_metadata=d["url_metadata"],
            time_ut=int(round(float(d["time_ut"]), 0)),
        )

    @classmethod
    def get_metadata_d_list(cls, force=True):
        if not os.path.exists(cls.LOCAL_METADATA_PATH) or force:
            os.makedirs("data", exist_ok=True)
            content = WWW(cls.URL_METADATA).read()
            File(cls.LOCAL_METADATA_PATH).write(content)
        d_list = TSVFile(cls.LOCAL_METADATA_PATH).read()
        en_d_list = [item for item in d_list if item.get("lang") == "en"]
        return en_d_list

    @classmethod
    def list_all(cls):
        d_list = cls.get_metadata_d_list()
        return [cls.from_dict(d) for d in d_list]
