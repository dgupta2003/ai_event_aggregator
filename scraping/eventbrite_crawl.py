# code to experiment with crawl4ai
import asyncio
import csv
import json
import os
import re
import codecs
from datetime import datetime
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler

def decode_unicode_escapes(text):
    """Decode Unicode escape sequences like \\u2013 and \\u0026"""
    if not text:
        return text
    
    # Manual replacements for common Unicode escape sequences
    replacements = {
        '\\u2013': '–',  # en-dash
        '\\u2014': '—',  # em-dash
        '\\u0026': '&',  # ampersand
        '\\u00a0': ' ',  # non-breaking space
        '\\u201c': '"',  # left double quotation mark
        '\\u201d': '"',  # right double quotation mark
        '\\u2019': "'",  # right single quotation mark
        '\\u2018': "'",  # left single quotation mark
        '\\u00e9': 'é',  # e with acute
        '\\u00f1': 'ñ',  # n with tilde
        '\\u2022': '•',  # bullet point
    }
    
    result = text
    for escape, replacement in replacements.items():
        result = result.replace(escape, replacement)
    
    return result

# --- start URLs: event listing pages -->
start_urls = [
    "https://www.eventbrite.com/d/ny--new-york/events--this-month/tech/",  # NYC tech events
    #"https://www.eventbrite.com/d/ny--new-york/business/",  # NYC business events (often tech-related)
    #"https://www.eventbrite.com/d/ny--new-york/science--tech/",  # NYC science & tech
    # Add more NYC tech-related URLs
]

async def fetch_and_extract():
    results = []
    crawled_urls = set()
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Process listing pages first - iterate through all pages
        for base_url in start_urls:
            page = 1
            max_pages = 25  # From the pagination data we saw: "page_count":25
            
            while page <= max_pages:
                # Construct URL for current page
                if page == 1:
                    url = base_url
                else:
                    url = f"{base_url}?page={page}"
                    
                if url in crawled_urls:
                    continue
                crawled_urls.add(url)
                
                print(f"Crawling listing page {page}/{max_pages}: {url}")
                result = await crawler.arun(
                    url=url, 
                    js_code=[
                        "window.scrollTo(0, document.body.scrollHeight);",
                        "await new Promise(resolve => setTimeout(resolve, 3000));",  # Wait 3 seconds
                        "window.scrollTo(0, document.body.scrollHeight);"  # Scroll again
                    ],
                    wait_for="css:.card-container, .search-base-root, [data-testid='event-card'], .event-card"
                )
            
                if not result.success:
                    print(f"Failed to crawl {url}: {result.error_message}")
                    page += 1
                    continue
                # Parse the HTML to extract event links
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.html, 'html.parser')
                
                # Debug: Save HTML to see the structure
                debug_dir = "debug_data"
                os.makedirs(debug_dir, exist_ok=True)
                debug_listing_file = os.path.join(debug_dir, "debug_eventbrite_listing.html")
                with open(debug_listing_file, "w", encoding="utf-8") as f:
                    f.write(result.html)
                print(f"Listing HTML saved to {debug_listing_file} for inspection")
                
                # Find event links
                event_links = []
                # Try different selectors for event cards
                link_selectors = [
                    "a[href*='/e/']",  # URLs containing /e/
                    ".eds-event-card-content__action-link",
                    "[data-testid='event-card'] a",
                    ".event-card a",
                    "a[data-testid]",  # Any link with data-testid
                    "a[href*='eventbrite.com']"  # Any eventbrite link
                ]
                
                for selector in link_selectors:
                    links = soup.select(selector)
                    print(f"Selector '{selector}' found {len(links)} links")
                    if links:
                        for link in links:
                            href = link.get('href')
                            print(f"  Found link: {href}")
                            if href and '/e/' in href:
                                if not href.startswith('http'):
                                    href = urljoin(url, href)
                                event_links.append(href)
                        if event_links:  # Break if we found event links
                            break
                
                print(f"Found {len(event_links)} event links total")
                
                # If no events found, we might have reached the end
                if len(event_links) == 0:
                    print(f"No event links found on page {page}, stopping pagination")
                    break
                
                # Crawl individual event pages
                for event_url in event_links:  # Process all events
                    if event_url in crawled_urls:
                        continue
                    crawled_urls.add(event_url)
                    
                    print(f"Crawling event: {event_url}")
                    event_result = await crawler.arun(
                        url=event_url,
                        js_code=[
                            "window.scrollTo(0, document.body.scrollHeight);",
                            "await new Promise(resolve => setTimeout(resolve, 3000));",  # Wait 3 seconds for dynamic content
                            "window.scrollTo(0, 0);",  # Scroll back to top
                            "await new Promise(resolve => setTimeout(resolve, 2000));",  # Wait 2 more seconds
                            "window.scrollTo(0, document.body.scrollHeight/2);",  # Scroll to middle
                            "await new Promise(resolve => setTimeout(resolve, 2000));"  # Final wait
                        ],
                        wait_for="css:.ticket-card, .price-display, .event-price, [data-automation='ticket-price'], body"
                    )
                    
                    if event_result.success:
                        event_soup = BeautifulSoup(event_result.html, 'html.parser')
                        
                        # Debug: Save individual event HTML for inspection
                        event_id = event_url.split('/e/')[-1].split('-')[0] if '/e/' in event_url else 'unknown'
                        debug_dir = "debug_data"
                        os.makedirs(debug_dir, exist_ok=True)
                        debug_filename = os.path.join(debug_dir, f"debug_event_{event_id}.html")
                        with open(debug_filename, "w", encoding="utf-8") as f:
                            f.write(event_result.html)
                        print(f"  Event HTML saved to {debug_filename}")
                        
                        # Debug: Show some key elements that are available
                        print(f"  Available h1 tags: {[h1.get_text().strip()[:30] for h1 in event_soup.find_all('h1')]}")
                        print(f"  Available time tags: {len(event_soup.find_all('time'))}")
                        print(f"  Elements with 'location' in class: {len(event_soup.find_all(class_=lambda x: x and 'location' in ' '.join(x).lower()))}")
                        print(f"  Elements with 'price' in class: {len(event_soup.find_all(class_=lambda x: x and 'price' in ' '.join(x).lower()))}")
                        
                        # Extract event details with more comprehensive fields
                        title = None
                        datetime_str = None
                        location = None
                        organizer = None
                        price = None
                        description = None
                        tags = None
                        event_type = None
                        venue_name = None
                        
                        # Try different selectors for title
                        title_selectors = [
                            "h1[data-automation='listing-title']",
                            "h1.event-title",
                            "h1",
                            ".event-hero-title h1"
                        ]
                        for selector in title_selectors:
                            title_elem = event_soup.select_one(selector)
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                break
                        
                        # Try different selectors for date/time with more comprehensive patterns
                        date_selectors = [
                            "[data-automation='event-date']",
                            ".event-date",
                            "[data-testid='event-date']",
                            ".date-info__full-datetime",
                            ".event-hero__date",
                            ".event-details__date",
                            "time",
                            ".structured-content time",
                            "[data-spec='event-date']",
                            ".summary .date",
                            "h2:contains('When')",
                            ".event-sidebar time"
                        ]
                        for selector in date_selectors:
                            date_elem = event_soup.select_one(selector)
                            if date_elem:
                                datetime_str = date_elem.get_text(strip=True)
                                print(f"  Found datetime with selector '{selector}': {datetime_str[:50]}...")
                                break
                        
                        # If no date found, try finding it in the page text
                        if not datetime_str:
                            # Look for common date patterns in text
                            page_text = event_soup.get_text()
                            import re
                            date_patterns = [
                                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
                                r'\d{1,2}/\d{1,2}/\d{4}',
                                r'\d{4}-\d{2}-\d{2}'
                            ]
                            for pattern in date_patterns:
                                match = re.search(pattern, page_text)
                                if match:
                                    datetime_str = match.group()
                                    print(f"  Found datetime with regex pattern: {datetime_str}")
                                    break
                        
                        # Try different selectors for location with more comprehensive patterns
                        location_selectors = [
                            "[data-automation='event-location']",
                            ".event-location",
                            "[data-testid='event-location']",
                            ".location-info__address",
                            ".event-hero__location",
                            ".event-details__location",
                            ".venue-address",
                            "[data-spec='event-location']",
                            ".summary .location",
                            "h2:contains('Where') + div",
                            ".event-sidebar .location",
                            ".location-info",
                            ".address"
                        ]
                        for selector in location_selectors:
                            location_elem = event_soup.select_one(selector)
                            if location_elem:
                                location = location_elem.get_text(strip=True)
                                # Clean up location text - remove "Get directions" and similar unwanted text
                                location = location.replace("Get directions", "").strip()
                                location = location.replace("View Map", "").strip()
                                location = location.replace("Directions", "").strip()
                                print(f"  Found location with selector '{selector}': {location[:50]}...")
                                break
                        
                        # Try different selectors for organizer with more comprehensive patterns
                        organizer_selectors = [
                            "a[data-automation='organizer-name']",
                            ".organizer-name",
                            "[data-testid='organizer-name']",
                            ".event-hero__organizer",
                            ".organizer-link",
                            ".event-organizer a",
                            "[data-spec='organizer-name']",
                            ".summary .organizer",
                            "h2:contains('Organizer') + div",
                            ".event-sidebar .organizer",
                            ".hosted-by a",
                            ".organizer-info a"
                        ]
                        
                        # First try from meta description (common pattern: "Organizer presents Event")
                        try:
                            meta_desc = event_soup.find('meta', {'name': 'description'})
                            if meta_desc and meta_desc.get('content'):
                                desc_text = meta_desc.get('content')
                                # Look for "X presents" or "X hosts" pattern
                                import re
                                patterns = [
                                    r'Eventbrite - ([^-]+) presents',
                                    r'Eventbrite - ([^-]+) hosts',
                                    r'([^-]+) presents [^-]+ -',
                                    r'hosted by ([^.]+)',
                                    r'presented by ([^.]+)'
                                ]
                                for pattern in patterns:
                                    match = re.search(pattern, desc_text, re.IGNORECASE)
                                    if match:
                                        organizer = match.group(1).strip()
                                        print(f"  Found organizer from meta description: {organizer}")
                                        break
                        except Exception as e:
                            pass
                        
                        # If not found in meta, try CSS selectors
                        if organizer == "N/A":
                            for selector in organizer_selectors:
                                organizer_elem = event_soup.select_one(selector)
                                if organizer_elem:
                                    organizer = organizer_elem.get_text(strip=True)
                                    print(f"  Found organizer with selector '{selector}': {organizer[:50]}...")
                                    break
                        
                        # Try different selectors for price with more comprehensive patterns
                        price_selectors = [
                            ".ticket-card .ticket-card__price",  # More specific ticket card price
                            ".ticket-card-content .conversion-bar__panel-info",  # Conversion bar price
                            "[data-automation='ticket-price']",
                            ".ticket-price",
                            "[data-testid='ticket-price']",
                            ".event-price",
                            ".price-display",
                            ".ticket-card__price",
                            ".event-hero__price",
                            "[data-spec='ticket-price']",
                            ".summary .price",
                            "h2:contains('Tickets') + div",
                            ".event-sidebar .price",
                            ".pricing-info",
                            ".cost",
                            ".ticket-info .price",
                            ".eds-ticket-card-content__price",
                            ".ticket-list .price",
                            "span:contains('$')",
                            "span:contains('Free')",
                            "span:contains('£')",
                            "span:contains('€')"
                        ]
                        
                                                # First try to find price in the __SERVER_DATA__ JavaScript variable (most reliable)
                        try:
                            script_tags = event_soup.find_all('script')
                            for script in script_tags:
                                if script.string and '__SERVER_DATA__' in script.string:
                                    script_content = script.string
                                    # Look for panelDisplayPrice in the server data
                                    display_price_match = re.search(r'"panelDisplayPrice":\s*"([^"]+)"', script_content)
                                    if display_price_match:
                                        price = display_price_match.group(1)
                                        print(f"  Found price in __SERVER_DATA__: {price}")
                                        break
                                    # Also look for statusToDisplay which is another price field
                                    status_display_match = re.search(r'"statusToDisplay":\s*"([^"]+)"', script_content)
                                    if status_display_match and '$' in status_display_match.group(1):
                                        price = status_display_match.group(1)
                                        print(f"  Found price in statusToDisplay: {price}")
                                        break
                        except Exception as e:
                            pass

                        # Fallback: Try other JSON data patterns
                        if price == "N/A":
                            try:
                                script_tags = event_soup.find_all('script')
                                for script in script_tags:
                                    if script.string and ('ticketPrice' in script.string or 'cost' in script.string):
                                        import json
                                        # Look for JSON objects containing price information
                                        script_content = script.string
                                        # Try to extract price from JSON-like structures
                                        if '\"cost\":' in script_content:
                                            # Extract cost value
                                            cost_match = re.search(r'\"cost\":\\s*\"([^\"]+)\"', script_content)
                                            if cost_match:
                                                price = cost_match.group(1)
                                                print(f"  Found price in JSON cost: {price}")
                                                break
                                        if '\"ticketPrice\":' in script_content:
                                            # Extract ticket price value
                                            price_match = re.search(r'\"ticketPrice\":\\s*\"([^\"]+)\"', script_content)
                                            if price_match:
                                                price = price_match.group(1)
                                                print(f"  Found price in JSON ticketPrice: {price}")
                                                break
                            except Exception as e:
                                pass
                        
                        # If not found in JSON, try CSS selectors
                        if price == "N/A":
                            for selector in price_selectors:
                                price_elem = event_soup.select_one(selector)
                                if price_elem:
                                    price = price_elem.get_text(strip=True)
                                    print(f"  Found price with selector '{selector}': {price[:50]}...")
                                    break
                        
                        # Try different selectors for description
                        desc_selectors = [
                            "div[data-automation='listing-event-description']",
                            ".event-description",
                            "[data-testid='event-description']",
                            ".structured-content-rich-text",
                            "section[data-automation='event-description']"
                        ]
                        for selector in desc_selectors:
                            desc_elem = event_soup.select_one(selector)
                            if desc_elem:
                                description = desc_elem.get_text(strip=True)
                                break
                        
                        # Try to extract tags/categories with more comprehensive patterns
                        tag_selectors = [
                            ".tags a",
                            ".event-tags span",
                            "[data-testid='event-tags'] span",
                            ".category-link",
                            ".event-categories a",
                            ".event-hero__tags span",
                            ".tag-list a",
                            "[data-spec='event-tags'] span",
                            ".summary .tags",
                            "h2:contains('Tags') + div a",
                            ".event-sidebar .tags span",
                            ".categories a",
                            ".labels span"
                        ]
                        
                        # Try to extract tags from JSON data (category/subcategory)
                        try:
                            script_tags = event_soup.find_all('script')
                            tag_list = []
                            for script in script_tags:
                                if script.string and '"category":' in script.string:
                                    # Look for category and subcategory in JSON
                                    category_match = re.search(r'"category":"([^"]+)"', script.string)
                                    subcategory_match = re.search(r'"subcategory":"([^"]+)"', script.string)
                                    if category_match:
                                        category = category_match.group(1).replace(' \\u0026 ', ' & ')
                                        tag_list.append(category)
                                    if subcategory_match:
                                        subcategory = subcategory_match.group(1)
                                        tag_list.append(subcategory)
                                    if tag_list:
                                        tags = ", ".join(tag_list)
                                        print(f"  Found tags from JSON data: {tags}")
                                        break
                        except Exception as e:
                            pass
                        
                        # If not found in JSON, try CSS selectors
                        if tags == "N/A":
                            for selector in tag_selectors:
                                tag_elems = event_soup.select(selector)
                                if tag_elems:
                                    tags = ", ".join([tag.get_text(strip=True) for tag in tag_elems])
                                    print(f"  Found tags with selector '{selector}': {tags[:50]}...")
                                    break
                        
                        # Try to extract venue name separately from location
                        venue_selectors = [
                            ".venue-name",
                            "[data-testid='venue-name']",
                            ".location-info__venue",
                            "h2[data-automation='venue-name']",
                            ".event-hero__venue",
                            ".venue-info h3",
                            ".venue-title",
                            "[data-spec='venue-name']",
                            ".summary .venue",
                            "h3:contains('Venue')",
                            ".event-sidebar .venue",
                            ".location-info__address p",  # Address paragraph - venue name is often first
                            ".location-info__address-text"  # Specific venue text element
                        ]
                        
                        # Try to extract venue name from JSON data first
                        try:
                            import re
                            script_tags = event_soup.find_all('script')
                            for script in script_tags:
                                if script.string and 'venueName' in script.string:
                                    # Look for JSON data with venue name
                                    venue_match = re.search(r'"venueName":"([^"]+)"', script.string)
                                    if venue_match:
                                        venue_name = venue_match.group(1)
                                        print(f"  Found venue from JSON data: {venue_name}")
                                        break
                        except Exception as e:
                            pass
                        
                        # If not found in JSON, try CSS selectors
                        if not venue_name:
                            for selector in venue_selectors:
                                venue_elem = event_soup.select_one(selector)
                                if venue_elem:
                                    venue_name = venue_elem.get_text(strip=True)
                                    print(f"  Found venue with selector '{selector}': {venue_name[:50]}...")
                                    break
                        
                        # Try to determine event type with more comprehensive patterns
                        event_type_selectors = [
                            "[data-automation='event-type']",
                            ".event-type",
                            ".category",
                            ".event-category",
                            ".event-hero__category",
                            "[data-spec='event-category']",
                            ".summary .category",
                            "h2:contains('Category') + div",
                            ".event-sidebar .category",
                            ".breadcrumb a:last-child",
                            ".tag"
                        ]
                        
                        # Try to extract event type from JSON data
                        try:
                            script_tags = event_soup.find_all('script')
                            for script in script_tags:
                                if script.string and '"format":' in script.string:
                                    # Look for event format or category in JSON
                                    format_match = re.search(r'"format":"([^"]+)"', script.string)
                                    category_match = re.search(r'"category":"([^"]+)"', script.string)
                                    if format_match:
                                        event_type = format_match.group(1)
                                        print(f"  Found event_type from JSON format: {event_type}")
                                        break
                                    elif category_match:
                                        event_type = category_match.group(1)
                                        print(f"  Found event_type from JSON category: {event_type}")
                                        break
                        except Exception as e:
                            pass
                        
                        # If not found in JSON, try CSS selectors
                        if event_type == "N/A":
                            for selector in event_type_selectors:
                                type_elem = event_soup.select_one(selector)
                                if type_elem:
                                    event_type = type_elem.get_text(strip=True)
                                    print(f"  Found event_type with selector '{selector}': {event_type[:50]}...")
                                    break
                        
                        event_data = {
                            "url": decode_unicode_escapes(event_url),
                            "title": decode_unicode_escapes(title or "N/A"),
                            "datetime": decode_unicode_escapes(datetime_str or "N/A"),
                            "location": decode_unicode_escapes(location or "N/A"),
                            "venue_name": decode_unicode_escapes(venue_name or "N/A"),
                            "organizer": decode_unicode_escapes(organizer or "N/A"),
                            "price": decode_unicode_escapes(price or "N/A"),
                            "event_type": decode_unicode_escapes(event_type or "N/A"),
                            "tags": decode_unicode_escapes(tags or "N/A"),
                            "description": decode_unicode_escapes(description or "N/A"),
                            "scraped_at": datetime.now().isoformat()
                        }
                        
                        results.append(event_data)
                        print(f"Extracted: {title}")
                
                # Move to next page after processing all events from current page
                page += 1
    
    return results

# Run the async fetcher and collect results
async def main():
    print("Starting Eventbrite scraping for NYC Tech events...")
    results = await fetch_and_extract()
    
    print(f"\nFound {len(results)} events")
    for item in results:
        print("FOUND:", item["title"])
    
    # Save results to both CSV and JSON with organized folder structure
    if results:
        # Generate timestamp for folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create organized directory structure: scraped_data/eventbrite/date
        base_dir = "scraped_data"
        eventbrite_dir = os.path.join(base_dir, "eventbrite")
        run_dir = os.path.join(eventbrite_dir, timestamp)
        os.makedirs(run_dir, exist_ok=True)
        
        # Define file paths
        csv_filename = os.path.join(run_dir, "nyc_tech_events.csv")
        json_filename = os.path.join(run_dir, "nyc_tech_events.json")
        
        # Save to CSV
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\nCSV results saved to {csv_filename}")
        
        # Save to JSON
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"JSON results saved to {json_filename}")
        
        print(f"\nTotal events scraped: {len(results)}")
        print(f"All files saved in: {run_dir}/")
    else:
        print("No events found to save.")

if __name__ == "__main__":
    asyncio.run(main())
