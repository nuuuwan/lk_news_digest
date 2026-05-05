import html as _html
import os
from datetime import datetime

from utils import Log

log = Log("NewsDigestBroadsheetMixin")

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
    _OTHER_NEWS_WORD_BUDGET = 400

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
    def _article_block(article, title_class, body_pt):
        title = _e(article["title"])
        body = _e(article.get("body", ""))
        html = f'<div class="article-title {title_class}">{title}</div>'
        if body:
            html += (
                f'<div class="article-body" style="font-size:{body_pt}pt">'
                f"{body}</div>"
            )
        return html

    def build_broadsheet(self, digest_article_list, ts, used_articles=None):
        # ── Date line ──────────────────────────────────────────────────────
        if used_articles:
            date_strs = sorted(a.date_str for a in used_articles)
            date_line = (
                f"{_fmt_date(date_strs[0])}  to  {_fmt_date(date_strs[-1])}"
                f"   \u00b7   AI-generated summary of {len(used_articles):,} articles"
            )
        else:
            date_line = ts

        # ── Article lists ──────────────────────────────────────────────────
        level0 = [a for a in digest_article_list if a.get("level") == 0]
        level1 = [a for a in digest_article_list if a.get("level") == 1]
        level2_all = [a for a in digest_article_list if a.get("level") == 2]
        level2 = self._cap_level2_by_budget(level2_all)
        level2_overflow = level2_all[len(level2) :]

        # ── Layout planning ────────────────────────────────────────────────
        n_l1_rows = (len(level1) + 2) // 3 if level1 else 0
        last_row_filled = len(level1) % 3
        overflow_slots = (3 - last_row_filled) % 3 if n_l1_rows else 0
        overflow_in_last_row = level2_overflow[:overflow_slots]
        overflow_extra = level2_overflow[overflow_slots:]
        n_extra_rows = (len(overflow_extra) + 2) // 3 if overflow_extra else 0

        total_content_rows = n_l1_rows + n_extra_rows
        if total_content_rows <= 1:
            body_pt = 16
        elif total_content_rows == 2:
            body_pt = 14
        elif total_content_rows == 3:
            body_pt = 13
        else:
            body_pt = 12

        # ── Sidebar ────────────────────────────────────────────────────────
        sidebar_items = "".join(
            self._article_block(a, "saffron", body_pt) for a in level2
        )
        sidebar_html = f"""
    <aside class="sidebar">
      <div class="section-label">OTHER NEWS</div>
      {sidebar_items}
    </aside>"""

        # ── Main grid ──────────────────────────────────────────────────────
        headline_title = _e(level0[0]["title"]) if level0 else ""
        headline_body = level0[0].get("body", "") if level0 else ""
        body_chunks = self._split_text(headline_body, 3)

        cells = []
        cells.append(f'<div class="headline-title">{headline_title}</div>')
        for chunk in body_chunks:
            cells.append(
                f'<div class="headline-body"'
                f' style="font-size:{body_pt}pt">{_e(chunk)}</div>'
            )
        for a in level1:
            cells.append(
                f'<div class="l1-cell">'
                f'{self._article_block(a, "green", body_pt)}</div>'
            )
        for a in overflow_in_last_row:
            cells.append(
                f'<div class="l1-cell overflow">'
                f'{self._article_block(a, "saffron", body_pt)}</div>'
            )
        for a in overflow_extra:
            cells.append(
                f'<div class="l1-cell overflow">'
                f'{self._article_block(a, "saffron", body_pt)}</div>'
            )

        main_html = (
            '<main class="main-grid">\n' + "\n".join(cells) + "\n</main>"
        )

        # ── Full HTML ──────────────────────────────────────────────────────
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>This Week in Sri Lanka \u2013 {_e(ts)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,400;0,700;1,400;1,700&display=swap"
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
      font-family: 'Ubuntu', sans-serif;
      font-size: {body_pt}pt;
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
      text-align: center;
      font-size: clamp(9pt, 1.2vw, 14pt);
      font-style: italic;
      color: var(--saffron);
      padding: 4pt 0;
    }}
    .page-grid {{
      display: grid;
      grid-template-columns: 25% 75%;
      gap: 0;
    }}
    /* ── Sidebar ── */
    .sidebar {{
      padding: 0 1% 0 0;
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
      padding-left: 1%;
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
    .article-title.saffron {{ font-size: clamp(8pt,  0.9vw, 12pt); color: var(--saffron); }}
    .article-title.green   {{ font-size: clamp(11pt, 1.6vw, 24pt); color: var(--green);   }}
    .article-body {{
      text-align: justify;
      margin-bottom: 10pt;
    }}
    /* ── Footer ── */
    footer {{
      margin-top: 14pt;
      text-align: center;
      font-size: 9pt;
      font-style: italic;
      color: var(--maroon);
    }}
    footer a {{ color: var(--maroon); text-decoration: none; }}
  </style>
</head>
<body>
  <header class="masthead">This Week in Sri Lanka</header>
  <div class="dateline-wrapper">
    <hr class="dateline-rule">
    <div class="dateline">{_e(date_line)}</div>
    <hr class="dateline-rule">
  </div>
  <div class="page-grid">
    {sidebar_html}
    {main_html}
  </div>
  <footer>
    <a href="https://github.com/nuuuwan/lk_news_digest">
      https://github.com/nuuuwan/lk_news_digest
    </a>
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
