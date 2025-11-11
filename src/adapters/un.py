from typing import List
from ..fetchers import fetch_html, soup_or_none
from ..models import Event
from ..utils import parse_date_safe

BASE = "https://www.un.org/en/events"

def run(query: str) -> List[Event]:
    html = fetch_html(BASE)
    soup = soup_or_none(html)
    if not soup:
        return []
    out: List[Event] = []
    cards = soup.select("a[href*='/en/']")
    for a in cards:
        title = a.get_text(" ", strip=True)
        href = a.get("href","")
        if not href or "/events/" not in href:
            continue
        url = "https://www.un.org" + href
        date = None
        parent = a.find_parent()
        if parent:
            t = parent.get_text(" ", strip=True)
            date = parse_date_safe(t)
        out.append(Event(source="un", title=title, url=url, start=date, country="Global"))
    return out
