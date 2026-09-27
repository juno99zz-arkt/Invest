"""
시장 브리핑용 뉴스 후보 수집 (RSS, 비용 없음).
Claude 가 웹검색으로 기사를 찾는 대신, 여기서 모은 실제 기사 목록 중에서 고르게 해
웹검색 횟수와 검색 결과로 불어나는 입력 토큰을 줄인다.
"""
import html
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

import feedparser
import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# 요약문이 들어 있는 언론사 피드
FEEDS = [
    ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),   # Top News
    ("CNBC", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),    # Economy
    ("CNBC", "https://www.cnbc.com/id/15839069/device/rss/rss.html"),    # Investing
    ("CNBC", "https://www.cnbc.com/id/19854910/device/rss/rss.html"),    # Technology
    ("MarketWatch", "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
]
# Google 뉴스 검색 (여러 언론사, 제목 끝의 ' - 언론사' 로 출처 표기)
QUERIES = [
    "stock market", "Federal Reserve interest rates", "inflation CPI jobs report",
    "AI chips data center spending", "earnings guidance", "S&P 500 Nasdaq outlook",
]
MAX_PER_SOURCE = 15
MAX_TOTAL = 70


def _get(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    return feedparser.parse(r.content)


def _date(entry):
    for key in ("published", "updated"):
        if entry.get(key):
            try:
                d = parsedate_to_datetime(entry[key])
                return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
            except (TypeError, ValueError):
                pass
    return None


def _clean(text, limit=280):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _norm(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())[:60]


def fetch_candidates(tickers=(), days=14):
    """최근 days일 기사 후보 [{id, title, source, url, published, snippet}] (최신순)."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    sources = list(FEEDS)
    sources += [(None, f"https://news.google.com/rss/search?q={quote(q + f' when:{days}d')}&hl=en-US&gl=US&ceid=US:en")
                for q in QUERIES]
    if tickers:
        q = " OR ".join(f"{t} stock" for t in tickers[:6])
        sources.append((None, f"https://news.google.com/rss/search?q={quote(f'({q}) when:{days}d')}&hl=en-US&gl=US&ceid=US:en"))

    items, seen = [], set()
    for source, url in sources:
        try:
            feed = _get(url)
        except Exception as e:  # 한 피드 실패는 무시
            print(f"  RSS 실패 ({url[:60]}): {e}")
            continue
        n = 0
        for e in feed.entries:
            title, link, d = _clean(e.get("title"), 300), e.get("link"), _date(e)
            if not title or not link or not d or d < cutoff:
                continue
            src = source
            if src is None:  # Google 뉴스: 'Headline - Source'
                src = (e.get("source") or {}).get("title")
                if " - " in title:
                    title, tail = title.rsplit(" - ", 1)
                    src = src or tail
            key = _norm(title)
            if key in seen:
                continue
            seen.add(key)
            snippet = _clean(e.get("summary")) if source else ""
            items.append({"title": title, "source": src or "", "url": link,
                          "published": d.date().isoformat(), "snippet": snippet, "_dt": d})
            n += 1
            if n >= MAX_PER_SOURCE:
                break

    items.sort(key=lambda x: x["_dt"], reverse=True)
    items = items[:MAX_TOTAL]
    for i, x in enumerate(items):
        x.pop("_dt")
        x["id"] = i
    print(f"  뉴스 후보 {len(items)}건 수집 (RSS)")
    return items


if __name__ == "__main__":
    for x in fetch_candidates(["NVDA"])[:10]:
        print(x["published"], x["source"], "|", x["title"])
