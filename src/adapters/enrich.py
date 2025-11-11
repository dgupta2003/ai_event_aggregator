from typing import List
from ..models import Event
from ..utils import parse_date_safe, clean_text
from ..fetchers import fetch_html, soup_or_none
from ._jsonld import events_from_jsonld

def enrich_with_details(events: List[Event], max_fetch: int = 8) -> List[Event]:
    need = [e for e in events if (e.start is None or (not e.city and not e.region)) and (e.url or "").startswith("http")]
    for e in need[:max_fetch]:
        html = fetch_html(e.url)
        soup = soup_or_none(html)
        if not soup:
            continue
        jd = events_from_jsonld(soup, e.source)
        if jd:
            best = jd[0]
            e.start = e.start or best.start
            e.city = e.city or best.city
            e.region = e.region or best.region
            e.raw = e.raw or best.raw
        if e.start is None:
            date_el = soup.select_one("time, .event-date, [itemprop='startDate']")
            if date_el:
                e.start = parse_date_safe(date_el.get_text(" ", strip=True))
        if not e.city and not e.region:
            loc_el = soup.select_one("[data-testid*='location'], .event-location, [itemprop='location']")
            if loc_el:
                txt = clean_text(loc_el.get_text(" ", strip=True))
                if "," in txt:
                    parts = [p.strip() for p in txt.split(",")]
                    if parts:
                        e.city = parts[0]
                    if len(parts) > 1:
                        e.region = parts[1][:2]
    return events

