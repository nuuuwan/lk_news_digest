import base64
import html as _html
import os
from datetime import datetime

from utils import Log

log = Log("NewsDigestBroadsheetMixin")

_QR_PATH = os.path.join("images", "qr.png")


def _qr_data_uri():
    """Return the QR code as an inline base64 data URI."""
    try:
        with open(_QR_PATH, "rb") as f:
            return (
                "data:image/png;base64," + base64.b64encode(f.read()).decode()
            )
    except FileNotFoundError:
        return ""


# Sri Lanka flag colour palette
_MAROON = "#8D153A"
_SAFFRON = "#FC8B00"
_GREEN = "#00534E"
_BLACK = "#000000"


def _ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{['th','st','nd','rd','th','th','th','th','th','th'][n % 10]}"


def _fmt_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.strftime('%A')} the {_ordinal(dt.day)} of {dt.strftime('%B, %Y')}"


def _e(text):
    return _html.escape(str(text))


class NewsDigestBroadsheetMixin:
    DIR_BROADSHEETS = os.path.join("data", "broadsheets")
    _OTHER_NEWS_WORD_BUDGET = 2000

    def _cap_level2_by_budget(self, articles):
        result, used = [], 0
        for article in articles:
            words = len(article["title"].split()) + len(
                article.get("body", "").split()
            )
            if used + words > self._OTHER_NEWS_WORD_BUDGET:
                break
            result.append(article)
            used += words
        return result

    @staticmethod
    def _split_text(text, n):
        words = text.split()
        if not words:
            return [""] * n
        chunk_size = max(1, len(words) // n)
        chunks = []
        for i in range(n):
            start = i * chunk_size
            end = start + chunk_size if i < n - 1 else len(words)
            chunks.append(" ".join(words[start:end]))
        return chunks

    @staticmethod
    def _article_block(article, title_class):
        title = _e(article["title"])
        body = _e(article.get("body", ""))
        html = f'<div class="article-title {title_class}">{title}</div>'
        if body:
            html += f'<div class="article-body">{body}</div>'
        return html

    def build_broadsheet(self, digest_article_list, ts, used_articles=None):
        # ── Date line ──────────────────────────────────────────────────────
        if used_articles:
            date_strs = sorted(a.date_str for a in used_articles)
            end_dt = datetime.strptime(date_strs[-1], "%Y-%m-%d")
            week_num = end_dt.isocalendar()[1]
            year = end_dt.year
            # end date without year: e.g. "Tuesday the 5th of May"
            end_no_year = f"{end_dt.strftime('%A')} the {_ordinal(end_dt.day)} of {end_dt.strftime('%B')}"
            dateline_left = f"Week {week_num}, {year}"
            dateline_center = f"{end_no_year}"
            dateline_right = f"AI Summary of {len(used_articles):,} Articles"
        else:
            dateline_left = ""
            dateline_center = ts
            dateline_right = ""

        # ── Article lists ──────────────────────────────────────────────────
        level0 = [a for a in digest_article_list if a.get("level") == 0]
        level1 = [a for a in digest_article_list if a.get("level") == 1]
        level2_all = [a for a in digest_article_list if a.get("level") == 2]
        level2 = self._cap_level2_by_budget(level2_all)
        level2_left = level2[:3]
        level2_sidebar = level2[3:]
        level2_overflow = level2_all[len(level2) :]

        # ── Layout planning ────────────────────────────────────────────────
        n_l1_rows = (len(level1) + 2) // 3 if level1 else 0
        last_row_filled = len(level1) % 3
        overflow_slots = (3 - last_row_filled) % 3 if n_l1_rows else 0
        overflow_in_last_row = level2_overflow[:overflow_slots]
        overflow_extra = level2_overflow[overflow_slots:]
        n_extra_rows = (len(overflow_extra) + 2) // 3 if overflow_extra else 0

        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar_items = "".join(
            self._article_block(a, "green") for a in level2_sidebar
        )
        sidebar_html = f"""
    <aside class="sidebar">
      {sidebar_items}
    </aside>"""

        # ── Main grid ──────────────────────────────────────────────────────
        headline_title = _e(level0[0]["title"]) if level0 else ""
        headline_body = level0[0].get("body", "") if level0 else ""
        body_chunks = self._split_text(headline_body, 3)

        cells = []
        cells.append(f'<div class="headline-title">{headline_title}</div>')
        for chunk in body_chunks:
            cells.append(f'<div class="headline-body">{_e(chunk)}</div>')
        for a in level1:
            cells.append(
                f'<div class="l1-cell">'
                f'{self._article_block(a, "saffron")}</div>'
            )
        for a in level2_left:
            cells.append(
                f'<div class="l1-cell">'
                f'{self._article_block(a, "green")}</div>'
            )
        for a in overflow_in_last_row:
            cells.append(
                f'<div class="l1-cell overflow">'
                f'{self._article_block(a, "green")}</div>'
            )
        for a in overflow_extra:
            cells.append(
                f'<div class="l1-cell overflow">'
                f'{self._article_block(a, "green")}</div>'
            )

        main_html = (
            '<main class="main-grid">\n' + "\n".join(cells) + "\n</main>"
        )

        # ── Full HTML ──────────────────────────────────────────────────────
        qr_uri = _qr_data_uri()
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>This Week in Sri Lanka \u2013 {_e(ts)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400;1,600&display=swap"
        rel="stylesheet">
  <link href="https://fonts.cdnfonts.com/css/chomsky" rel="stylesheet">
  <style>
    :root {{
      --maroon:  {_MAROON};
      --saffron: {_SAFFRON};
      --green:   {_GREEN};
      --black:   {_BLACK};
    }}
    @page {{ size: A2 landscape; margin: 1in; }}
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Lora', serif;
      font-size: clamp(9pt, 1vw, 12pt);
      color: var(--black);
      background: #fff;
      max-width: 100%;
      padding: 2%;
    }}
    header.masthead {{
      text-align: center;
      font-family: 'Chomsky', serif;
      font-size: clamp(28pt, 5vw, 72pt);
      font-weight: normal;
      color: var(--maroon);
      margin-bottom: 6pt;
      line-height: 1.1;
    }}
    .dateline-wrapper {{
      margin: 6pt 0 14pt;
    }}
    .dateline-rule {{
      border: none;
      border-top: 2px solid var(--maroon);
      margin: 4pt 0;
    }}
    .dateline {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      font-size: clamp(9pt, 1.2vw, 14pt);
      font-style: italic;
      text-transform: uppercase;
      color: var(--saffron);
      padding: 4pt 0;
    }}
    .dateline-left  {{ text-align: left;   flex: 1; }}
    .dateline-center {{ text-align: center; flex: 2; }}
    .dateline-right {{ text-align: right;  flex: 1; }}
    .page-grid {{
      display: grid;
      grid-template-columns: 75% 25%;
      gap: 0;
      align-items: start;
    }}
    /* ── Sidebar ── */
    .sidebar {{
      padding: 0 0 0 1%;
    }}
    .section-label {{
      font-size: clamp(9pt, 1vw, 14pt);
      font-weight: bold;
      color: var(--green);
      margin-bottom: 8pt;
    }}
    /* ── Main 3-column grid ── */
    .main-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      column-gap: 1%;
      padding-right: 1%;
    }}
    .headline-title {{
      grid-column: 1 / 4;
      font-size: clamp(18pt, 3vw, 48pt);
      font-weight: bold;
      color: var(--maroon);
      line-height: 1.1;
      margin-bottom: 10pt;
    }}
    .headline-body {{
      text-align: justify;
      margin-bottom: 14pt;
    }}
    .l1-cell {{
      margin-top: 10pt;
    }}
    /* ── Article title variants ── */
    .article-title {{
      font-weight: bold;
      margin-bottom: 4pt;
      line-height: 1.2;
    }}
    .article-title.maroon {{ font-size: clamp(18pt, 3vw, 48pt);  color: var(--maroon);  }}
    .article-title.saffron {{ font-size: clamp(11pt, 1.6vw, 24pt); color: var(--saffron); }}
    .article-title.green   {{ font-size: clamp(8pt,  0.9vw, 12pt); color: var(--green);   }}
    .article-body {{
      text-align: justify;
      margin-bottom: 10pt;
    }}
    .article-title.green ~ .article-body {{
      font-size: clamp(7pt, 0.8vw, 10pt);
    }}
    /* ── Footer ── */
    footer {{
      margin-top: 14pt;
      border-top: 1px solid var(--maroon);
      padding-top: 6pt;
      text-align: center;
      font-size: 9pt;
      font-style: italic;
      color: var(--maroon);
    }}
    footer a {{ color: var(--maroon); text-decoration: none; }}
    /* ── Masthead with QR ── */
    .masthead-wrapper {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 6pt;
    }}
    .masthead-wrapper header.masthead {{
      margin-bottom: 0;
      flex: 1;
      text-align: center;
    }}
    .masthead-qr {{
      width: clamp(40px, 6vw, 90px);
      height: auto;
      flex-shrink: 0;
    }}
  </style>
</head>
<body>
  <div class="masthead-wrapper">
    <img class="masthead-qr" src="{qr_uri}" alt="QR code">
    <header class="masthead">This Week in Sri Lanka</header>
    <img class="masthead-qr" src="{qr_uri}" alt="QR code">
  </div>
  <div class="dateline-wrapper">
    <hr class="dateline-rule">
    <div class="dateline">
      <span class="dateline-left">{_e(dateline_left)}</span>
      <span class="dateline-center">{_e(dateline_center)}</span>
      <span class="dateline-right">{_e(dateline_right)}</span>
    </div>
    <hr class="dateline-rule">
  </div>
  <div class="page-grid">
    {main_html}
    {sidebar_html}
  </div>
  <footer>
    This broadsheet is an AI-generated weekly summary of news from Sri Lanka,
    compiled from articles across multiple sources and condensed using large
    language models. It is intended as a quick overview and may not reflect the
    full context of each story. For more details, see
    <a href="https://github.com/nuuuwan/lk_news_digest">https://github.com/nuuuwan/lk_news_digest</a>.
  </footer>
</body>
</html>"""

        os.makedirs(self.DIR_BROADSHEETS, exist_ok=True)
        broadsheet_path = os.path.join(
            self.DIR_BROADSHEETS, f"broadsheet.{ts}.html"
        )
        with open(broadsheet_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        log.info(f"Wrote broadsheet to {broadsheet_path}")
