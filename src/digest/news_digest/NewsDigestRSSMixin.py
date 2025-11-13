import re
from xml.dom import minidom
from xml.etree.ElementTree import (Element, SubElement, register_namespace,
                                   tostring)

from utils import Log, Time, TimeFormat

log = Log("NewsDigest")


class NewsDigestRSSMixin:
    DIGEST_RSS_PATH = "rss.xml"

    @staticmethod
    def get_deep_link_for_title(title: str) -> str:
        title = re.sub(r"[^a-zA-Z0-9 ]", "", title)
        title = title.replace(" ", "-").lower()
        return title

    def build_rss_header(self, used_articles, pub_time_str):
        register_namespace("atom", "http://www.w3.org/2005/Atom")
        rss = Element(
            "rss",
            {"version": "2.0"},
        )
        channel = SubElement(rss, "channel")
        SubElement(
            channel,
            "{http://www.w3.org/2005/Atom}link",
            {
                "href": self.RSS_FEED_URL,
                "rel": "self",
                "type": "application/rss+xml",
            },
        )

        for tag, text in [
            ("title", self.get_title()),
            ("link", self.URL),
            ("description", self.get_description(used_articles)),
            (
                "lastBuildDate",
                pub_time_str,
            ),
        ]:
            SubElement(channel, tag).text = text

        return rss, channel

    def build_rss_for_articles(
        self, rss, channel, digest_article_list, pub_time_str, ts
    ):

        history_url = self.get_history_url(ts)
        for i_article, digest_article in enumerate(
            digest_article_list, start=1
        ):
            item = SubElement(channel, "item")
            SubElement(item, "title").text = digest_article["title"]
            SubElement(item, "description").text = digest_article["body"]
            SubElement(item, "pubDate").text = pub_time_str
            deep_link_title = self.get_deep_link_for_title(
                digest_article["title"]
            )
            guid = f"{history_url}#{i_article}-{deep_link_title}"
            SubElement(item, "guid").text = guid

        return rss

    def build_rss_xml_data(self, used_articles, digest_article_list, ut, ts):
        pub_time_str = TimeFormat("%a, %d %b %Y %H:%M:%S %z").format(Time(ut))

        rss, channel = self.build_rss_header(used_articles, pub_time_str)
        rss = self.build_rss_for_articles(
            rss, channel, digest_article_list, pub_time_str, ts
        )

        rough = tostring(rss, encoding="utf-8", xml_declaration=True)
        parsed = minidom.parseString(rough)
        return parsed.toprettyxml(indent="  ", encoding="utf-8")

    def build_rss(self, used_articles, digest_article_list, ut, ts):
        rss_xml_data = self.build_rss_xml_data(
            used_articles, digest_article_list, ut, ts
        )
        with open(self.DIGEST_RSS_PATH, "wb") as f:
            f.write(rss_xml_data)
        log.info(f"Wrote {self.DIGEST_RSS_PATH}")
