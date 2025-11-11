from typing import List
from urllib.parse import quote_plus
from ..fetchers import fetch_html, soup_or_none
from ..models import Event
from ..utils import parse_date_safe, clean_text
from ._jsonld import events_from_jsonld
from .enrich import enrich_with_details

BASE = "https://www.meetup.com/find/?eventType=upcoming&keywords="

def run(query: str, near: str = None) -> List[Event]:
    url = BASE + quote_plus(query)
    if near:
        url += f"&source=EVENTS&location={quote_plus(near)}"
    html = fetch_html(url)
    soup = soup_or_none(html)
    if not soup:
        return []
    out: List[Event] = []
    j = events_from_jsonld(soup, "meetup")
    if j:
        out.extend(j)
    items = soup.select("a[href*='/events/']")
    for a in items:
        title = clean_text(a.get_text(" ", strip=True))
        href = a.get("href", "")
        if not href:
            continue
        full = href if href.startswith("http") else "https://www.meetup.com" + href
        dt = None
        parent = a.find_parent()
        if parent:
            t = clean_text(parent.get_text(" ", strip=True))
            dt = parse_date_safe(t)
        out.append(Event(source="meetup", title=title, url=full, start=dt))
    out = enrich_with_details(out, max_fetch=8)
    return out

