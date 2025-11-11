from typing import List
from ..fetchers import fetch_html, soup_or_none
from ..models import Event
from ..utils import parse_date_safe, clean_text
from .enrich import enrich_with_details

BASE = "https://www.ted.com/tedx/events"

def run(query: str) -> List[Event]:
    html = fetch_html(BASE)
    soup = soup_or_none(html)
    if not soup:
        return []
    out: List[Event] = []
    items = soup.select("a[href*='/tedx/events/']")
    for a in items:
        title = clean_text(a.get_text(" ", strip=True))
        url = "https://www.ted.com" + a.get("href","")
        dt = None
        parent = a.find_parent()
        if parent:
            t = clean_text(parent.get_text(" ", strip=True))
            dt = parse_date_safe(t)
        out.append(Event(source="tedx", title=title, url=url, start=dt))
    out = enrich_with_details(out, max_fetch=8)
    return out

