from typing import Optional
from bs4 import BeautifulSoup
import os
import requests

USE_CRAWL4AI = os.getenv("USE_CRAWL4AI", "1") != "0"

try:
    from crawl4ai import WebCrawler
    _has_c4 = True
except Exception:
    _has_c4 = False

def fetch_html(url: str, timeout: int = 25) -> Optional[str]:
    if USE_CRAWL4AI and _has_c4:
        try:
            crawler = WebCrawler()
            result = crawler.run(url=url, timeout=timeout)
            if result and getattr(result, "html", None):
                print(f"[Crawl4AI] {url}")
                return result.html
        except Exception as e:
            print(f"[Crawl4AI-Fallback] {url} reason={type(e).__name__}")
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if r.ok:
            print(f"[requests] {url}")
            return r.text
    except Exception:
        return None
    return None

def soup_or_none(html: Optional[str]) -> Optional[BeautifulSoup]:
    if not html:
        return None
    return BeautifulSoup(html, "lxml")

