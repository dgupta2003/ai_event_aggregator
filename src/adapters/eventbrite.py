from typing import List
from urllib.parse import urlencode
from ..fetchers import fetch_html, soup_or_none
from ..models import Event
from ..utils import parse_date_safe, clean_text
from ._jsonld import events_from_jsonld
from .enrich import enrich_with_details

def build_url(query: str, filters: dict) -> str:
    topic = query
    city = (filters.get("location_city") or "").lower().replace(" ", "-")
    region = (filters.get("location_region") or "").lower()
    if city and region:
        base = f"https://www.eventbrite.com/d/{region}--{city}/events/"
    else:
        base = "https://www.eventbrite.com/d/online/events/"
    params = {"q": topic}
    if filters.get("date_from"):
        params["start_date"] = filters["date_from"]
    if filters.get("date_to"):
        params["end_date"] = filters["date_to"]
    return f"{base}?{urlencode(params)}"

def parse(html: str) -> List[Event]:
    soup = soup_or_none(html)
    if not soup:
        return []
    jd = events_from_jsonld(soup, "eventbrite")
    if jd:
        return jd
    out: List[Event] = []
    cards = soup.select("[data-component='search-event-card'], div.eds-event-card-content__content")
    for c in cards:
        title_el = c.select_one("[data-spec='event-card__title'] a, .eds-event-card-content__title a")
        url_el = title_el or c.select_one("a[href]")
        date_el = c.select_one("time, .eds-text-bs--fixed")
        loc_el = c.select_one("[data-spec='event-card__subcontent']")
        title = clean_text(title_el.get_text(strip=True)) if title_el else ""
        url = url_el.get("href") if url_el else ""
        dt = parse_date_safe(date_el.get_text(" ", strip=True)) if date_el else None
        city = region = None
        if loc_el:
            loc_text = clean_text(loc_el.get_text(" ", strip=True))
            if "," in loc_text:
                parts = [p.strip() for p in loc_text.split(",")]
                if parts:
                    city = parts[0]
                if len(parts) > 1:
                    region = parts[1][:2]
        out.append(Event(source="eventbrite", title=title, url=url, start=dt, city=city, region=region))
    return out

def run(query: str, filters: dict = None) -> List[Event]:
    filters = filters or {}
    url = build_url(query, filters)
    html = fetch_html(url)
    if not html:
        return []
    events = parse(html)
    events = enrich_with_details(events, max_fetch=8)
    return events

