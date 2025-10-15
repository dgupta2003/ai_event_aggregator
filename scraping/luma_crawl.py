# Luma event scraper for NYC tech events
import asyncio
import csv
import json
import os
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup

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

# Luma URLs for NYC tech events
start_urls = [
    "https://luma.com/nyc",  # Main NYC events page - contains all events including tech
    # Note: Luma doesn't seem to have separate category filtering URLs like the old format
    # We'll extract all events and filter for tech-related ones based on content
]

async def fetch_and_extract():
    results = []
    crawled_urls = set()
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        # Process each category of events
        for base_url in start_urls:
            print(f"Crawling Luma category: {base_url}")
            
            # Add delay to avoid rate limiting
            await asyncio.sleep(2)
            
            result = await crawler.arun(
                url=base_url,
                js_code=[
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "await new Promise(resolve => setTimeout(resolve, 3000));",  # Wait for dynamic loading
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "await new Promise(resolve => setTimeout(resolve, 2000));",  # Additional wait
                    # Try to load more events by clicking "Load More" if it exists
                    "const loadMore = document.querySelector('[data-testid=\"load-more\"], .load-more, button:contains(\"Load more\")');",
                    "if (loadMore) { loadMore.click(); await new Promise(resolve => setTimeout(resolve, 3000)); }",
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "await new Promise(resolve => setTimeout(resolve, 2000));"
                ],
                wait_for="css:.event-card, [data-testid='event-card'], .event-item, body"
            )
            
            if not result.success:
                print(f"Failed to crawl {base_url}: {result.error_message}")
                continue
                
            # Parse the HTML to extract event links
            soup = BeautifulSoup(result.html, 'html.parser')
            
            # Debug: Save HTML to see the structure
            debug_dir = "debug_data"
            os.makedirs(debug_dir, exist_ok=True)
            category_name = 'nyc_all'  # Since we're scraping the main NYC page
            debug_listing_file = os.path.join(debug_dir, f"debug_luma_listing_{category_name}.html")
            with open(debug_listing_file, "w", encoding="utf-8") as f:
                f.write(result.html)
            print(f"Listing HTML saved to {debug_listing_file} for inspection")
            
            # Find event links - Luma uses pattern https://luma.com/{event-id}
            event_links = []
            link_selectors = [
                "a[href*='luma.com/']",  # Any luma.com link
                "a[href^='/']",  # Relative links that might be event URLs
                "a[href]"  # All links with href attribute
            ]
            
            for selector in link_selectors:
                links = soup.select(selector)
                print(f"Selector '{selector}' found {len(links)} links")
                for link in links:
                    href = link.get('href')
                    if href:
                        # Handle relative URLs
                        if not href.startswith('http'):
                            href = urljoin(base_url, href)
                        
                        # Filter for actual event URLs (luma.com/{event-id} format)
                        # Event IDs are typically short alphanumeric strings
                        if 'luma.com/' in href:
                            # Extract the path after luma.com/
                            path = href.split('luma.com/')[-1]
                            # Check if it looks like an event ID (short alphanumeric, not a page like 'discover', 'pricing', etc.)
                            if (len(path) > 3 and len(path) < 15 and 
                                path.isalnum() and 
                                path not in ['discover', 'pricing', 'help', 'create', 'signin', 'nyc', 'ios'] and
                                href not in event_links):
                                event_links.append(href)
                                print(f"  Found event link: {href}")
                
                # Break after first selector that finds events to avoid duplicates
                if event_links:
                    break
            
            # Also try to find events in JSON data embedded in the page
            try:
                script_tags = soup.find_all('script')
                for script in script_tags:
                    if script.string and ('event' in script.string.lower() and 'url' in script.string):
                        # Look for event URLs in JSON data (new luma.com format)
                        event_url_pattern = r'https://luma\.com/[a-zA-Z0-9]+'
                        found_urls = re.findall(event_url_pattern, script.string)
                        for url in found_urls:
                            # Extract the event ID and validate it looks like an event
                            event_id = url.split('luma.com/')[-1]
                            if (len(event_id) > 3 and len(event_id) < 15 and 
                                event_id.isalnum() and 
                                event_id not in ['discover', 'pricing', 'help', 'create', 'signin', 'nyc', 'ios'] and
                                url not in event_links):
                                event_links.append(url)
                                print(f"  Found event URL in JSON: {url}")
            except Exception as e:
                print(f"  Error parsing JSON for event URLs: {e}")
            
            print(f"Found {len(event_links)} total event links for category {category_name}")
            
            # Remove duplicates
            event_links = list(set(event_links))
            
            # Crawl individual event pages
            for event_url in event_links[:50]:  # Limit to 50 events per category to avoid rate limiting
                if event_url in crawled_urls:
                    continue
                crawled_urls.add(event_url)
                
                print(f"Crawling Luma event: {event_url}")
                
                # Add delay between requests to avoid rate limiting
                await asyncio.sleep(1)
                
                event_result = await crawler.arun(
                    url=event_url,
                    js_code=[
                        "window.scrollTo(0, document.body.scrollHeight);",
                        "await new Promise(resolve => setTimeout(resolve, 2000));",
                        "window.scrollTo(0, 0);",
                        "await new Promise(resolve => setTimeout(resolve, 1000));"
                    ],
                    wait_for="css:.event-details, .event-header, .event-info, body"
                )
                
                if event_result.success:
                    event_soup = BeautifulSoup(event_result.html, 'html.parser')
                    
                    # Debug: Save individual event HTML
                    event_id = event_url.split('/')[-1] if '/' in event_url else 'unknown'
                    debug_filename = os.path.join(debug_dir, f"debug_luma_event_{event_id}.html")
                    with open(debug_filename, "w", encoding="utf-8") as f:
                        f.write(event_result.html)
                    print(f"  Event HTML saved to {debug_filename}")
                    
                    # Extract event details
                    event_data = extract_luma_event_details(event_soup, event_url)
                    if event_data and event_data['title'] != 'N/A':
                        results.append(event_data)
                        print(f"  Extracted: {event_data['title']}")
                    else:
                        print(f"  Failed to extract event data from {event_url}")
    
    return results

def extract_luma_event_details(soup, event_url):
    """Extract event details from Luma event page"""
    
    # Initialize all fields
    title = None
    datetime_str = None
    location = None
    organizer = None
    price = None
    registration_type = None
    description = None
    tags = None
    event_type = None
    venue_name = None
    
    # Extract title
    title_selectors = [
        "h1",
        ".event-title",
        "[data-testid='event-title']",
        ".event-header h1",
        ".event-name",
        "title"  # Fallback to page title
    ]
    
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            title = title_elem.get_text(strip=True)
            if title and len(title) > 5:  # Ensure it's not just a short generic title
                break
    
    # Extract datetime
    datetime_selectors = [
        "[data-testid='event-date']",
        ".event-date",
        ".event-time",
        ".date-time",
        "time",
        ".when",
        ".event-datetime",
        ".schedule"
    ]
    
    for selector in datetime_selectors:
        date_elem = soup.select_one(selector)
        if date_elem:
            datetime_str = date_elem.get_text(strip=True)
            # Also check for datetime attribute
            if not datetime_str and date_elem.get('datetime'):
                datetime_str = date_elem.get('datetime')
            if datetime_str:
                break
    
    # Extract location
    location_selectors = [
        "[data-testid='event-location']",
        ".event-location",
        ".location",
        ".venue",
        ".where",
        ".event-venue",
        ".address",
        ".event-address"
    ]
    
    for selector in location_selectors:
        location_elem = soup.select_one(selector)
        if location_elem:
            location = location_elem.get_text(strip=True)
            if location:
                break
    
    # Extract organizer/host
    organizer_selectors = [
        "[data-testid='event-host']",
        ".event-host",
        ".organizer",
        ".host",
        ".hosted-by",
        ".event-organizer",
        ".creator"
    ]
    
    for selector in organizer_selectors:
        organizer_elem = soup.select_one(selector)
        if organizer_elem:
            organizer = organizer_elem.get_text(strip=True)
            if organizer:
                break
    
    # Extract price information
    price_selectors = [
        "[data-testid='event-price']",
        ".event-price",
        ".price",
        ".cost",
        ".ticket-price",
        ".pricing",
        ".fee"
    ]
    
    for selector in price_selectors:
        price_elem = soup.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            if price_text:
                # Extract actual price amount, not registration status
                price_match = re.search(r'\$(\d+(?:\.\d{2})?)', price_text)
                if price_match:
                    price = f"${price_match.group(1)}"
                elif any(word in price_text.lower() for word in ['free', 'no cost', 'complimentary']):
                    price = "Free"
                break
    
    # If no price found from dedicated selectors, look for "Free" indicators
    if not price:
        free_indicators = soup.find_all(string=re.compile(r'free|Free|FREE', re.IGNORECASE))
        if free_indicators:
            price = "Free"
    
    # Extract description
    desc_selectors = [
        "[data-testid='event-description']",
        ".event-description",
        ".description",
        ".event-details",
        ".about",
        ".event-about",
        ".content"
    ]
    
    for selector in desc_selectors:
        desc_elem = soup.select_one(selector)
        if desc_elem:
            description = desc_elem.get_text(strip=True)
            if description and len(description) > 20:  # Ensure it's substantial
                break
    
    # Enhanced tags/categories extraction from multiple sources
    tag_list = []
    
    # 1. Try HTML-based tag extraction first (most reliable when present)
    tag_selectors = [
        ".tags",
        ".categories", 
        ".event-tags",
        ".event-categories",
        ".labels",
        ".topics",
        "[data-testid*='tag']",
        "[data-testid*='category']"
    ]
    
    for selector in tag_selectors:
        tag_elems = soup.select(f"{selector} span, {selector} a, {selector} .tag, {selector} div")
        if tag_elems:
            for tag_elem in tag_elems:
                tag_text = tag_elem.get_text(strip=True)
                if tag_text and len(tag_text) < 50 and tag_text not in tag_list:  # Reasonable length check
                    tag_list.append(tag_text)
    
    # 2. Extract from JSON-LD structured data (most reliable source)
    if not tag_list:
        try:
            json_ld = soup.find('script', {'type': 'application/ld+json'})
            if json_ld and json_ld.string:
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    # Check for categories in JSON-LD
                    if data.get('category'):
                        categories = data.get('category')
                        if isinstance(categories, list):
                            tag_list.extend([cat for cat in categories if isinstance(cat, str)])
                        elif isinstance(categories, str):
                            tag_list.append(categories)
                    
                    # Check for keywords
                    if data.get('keywords'):
                        keywords = data.get('keywords')
                        if isinstance(keywords, str):
                            # Split comma-separated keywords
                            tag_list.extend([k.strip() for k in keywords.split(',') if k.strip()])
                        elif isinstance(keywords, list):
                            tag_list.extend([k for k in keywords if isinstance(k, str)])
        except Exception as e:
            pass
    
    # 3. Extract from other script tags with event data
    if not tag_list:
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and ('categories' in script.string or 'featured_infos' in script.string or 'tags' in script.string):
                try:
                    # Extract featured_infos
                    featured_match = re.search(r'"featured_infos":\s*\[([^\]]+)\]', script.string)
                    if featured_match:
                        featured_text = featured_match.group(1)
                        if 'Tech' in featured_text or 'AI' in featured_text:
                            tag_list.append('Tech')
                        if 'New York' in featured_text or 'NYC' in featured_text:
                            tag_list.append('NYC')
                    
                    # Look for explicit categories array
                    categories_match = re.search(r'"categories":\s*\[([^\]]+)\]', script.string)
                    if categories_match and categories_match.group(1).strip():
                        categories_text = categories_match.group(1)
                        category_names = re.findall(r'"name":\s*"([^"]+)"', categories_text)
                        tag_list.extend(category_names)
                    
                    # Look for tags array
                    tags_match = re.search(r'"tags":\s*\[([^\]]+)\]', script.string)
                    if tags_match and tags_match.group(1).strip():
                        tags_text = tags_match.group(1)
                        tag_names = re.findall(r'"([^"]+)"', tags_text)
                        tag_list.extend([tag for tag in tag_names if len(tag) > 2 and len(tag) < 30])
                    
                    break
                except Exception as e:
                    pass
    
    # 4. Content-based tag inference (comprehensive analysis)
    content_to_analyze = (title or "").lower() + " " + (description or "").lower()
    
    # Always add location tag for NYC events
    if 'new york' in content_to_analyze or 'nyc' in content_to_analyze or 'manhattan' in content_to_analyze:
        if 'NYC' not in tag_list:
            tag_list.append('NYC')
    
    # Tech-related tags (use word boundaries for short terms to avoid false positives)
    if any(keyword in content_to_analyze for keyword in ['artificial intelligence', 'machine learning']) or \
       re.search(r'\b(ai|ml)\b', content_to_analyze):
        if 'AI' not in tag_list:
            tag_list.append('AI')
    if any(keyword in content_to_analyze for keyword in ['startup', 'entrepreneur', 'founder', 'venture']):
        if 'Startups' not in tag_list:
            tag_list.append('Startups')
    if any(keyword in content_to_analyze for keyword in ['tech', 'technology', 'software', 'code', 'coding', 'programming', 'developer']):
        if 'Tech' not in tag_list:
            tag_list.append('Tech')
    
    # Industry/Interest tags
    if any(keyword in content_to_analyze for keyword in ['network', 'mixer', 'meetup']):
        if 'Networking' not in tag_list:
            tag_list.append('Networking')
    if any(keyword in content_to_analyze for keyword in ['art', 'creative', 'design', 'culture']):
        if 'Arts & Culture' not in tag_list:
            tag_list.append('Arts & Culture')
    if 'fitness' in content_to_analyze or 'workout' in content_to_analyze:
        if 'Fitness' not in tag_list:
            tag_list.append('Fitness')
    if 'wellness' in content_to_analyze or 'mindfulness' in content_to_analyze:
        if 'Wellness' not in tag_list:
            tag_list.append('Wellness')
    if any(keyword in content_to_analyze for keyword in ['workshop', 'training', 'course', 'learn']):
        if 'Workshop' not in tag_list:
            tag_list.append('Workshop')
    
    # Clean up and format tags
    if tag_list:
        # Remove duplicates and filter out generic/unhelpful tags
        tag_list = list(set([tag for tag in tag_list if tag and len(tag.strip()) > 1]))
        # Sort for consistency
        tag_list.sort()
        tags = ", ".join(tag_list)
    
    # Enhanced event type classification using multiple data sources
    event_type = "General"  # Default
    
    # First try to get event type from JSON-LD structured data
    try:
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld and json_ld.string:
            data = json.loads(json_ld.string)
            if isinstance(data, dict) and data.get('@type') == 'Event':
                # Check for explicit event category
                if data.get('category'):
                    category = data.get('category')
                    if isinstance(category, str):
                        event_type = category.title()
                    elif isinstance(category, list) and len(category) > 0:
                        event_type = category[0].title()
    except Exception as e:
        pass
    
    # If no structured data, analyze content
    if event_type == "General":
        content_to_check = (title or "").lower() + " " + (description or "").lower()
        
        # Prioritize by specificity (most specific first) - use word boundaries for short terms
        if any(keyword in content_to_check for keyword in ['artificial intelligence', 'machine learning', 'neural network', 'deep learning']) or \
           re.search(r'\b(ai|ml)\b', content_to_check):
            event_type = "AI"
        elif any(keyword in content_to_check for keyword in ['startup', 'entrepreneur', 'founder', 'venture', 'pitch', 'accelerator', 'incubator']):
            event_type = "Startup"
        elif any(keyword in content_to_check for keyword in ['workshop', 'training', 'course', 'learn', 'tutorial', 'bootcamp', 'masterclass']):
            event_type = "Workshop"
        elif any(keyword in content_to_check for keyword in ['tech', 'technology', 'software', 'code', 'coding', 'programming', 'developer', 'app', 'digital', 'web dev', 'data science']):
            event_type = "Technology"
        elif any(keyword in content_to_check for keyword in ['network', 'mixer', 'meetup', 'coffee', 'drinks', 'happy hour', 'social']):
            event_type = "Networking"
        elif any(keyword in content_to_check for keyword in ['conference', 'summit', 'symposium', 'panel', 'keynote']):
            event_type = "Conference"
        elif any(keyword in content_to_check for keyword in ['art', 'creative', 'design', 'culture', 'gallery', 'exhibition']):
            event_type = "Arts & Culture"
        elif any(keyword in content_to_check for keyword in ['fitness', 'workout', 'yoga', 'wellness', 'health']):
            event_type = "Wellness" if any(w in content_to_check for w in ['wellness', 'mindfulness', 'meditation']) else "Fitness"
        elif any(keyword in content_to_check for keyword in ['food', 'cooking', 'chef', 'restaurant', 'culinary']):
            event_type = "Food & Drink"
        elif any(keyword in content_to_check for keyword in ['music', 'concert', 'performance', 'show']):
            event_type = "Entertainment"
    
    # Extract venue name (often same as location but can be different)
    venue_selectors = [
        ".venue-name",
        ".event-venue-name",
        "[data-testid='venue-name']"
    ]
    
    for selector in venue_selectors:
        venue_elem = soup.select_one(selector)
        if venue_elem:
            venue_name = venue_elem.get_text(strip=True)
            break
    
    # If venue_name not found separately, extract from location
    if not venue_name and location:
        # Often venue name is the first part of location
        venue_name = location.split(',')[0].strip() if ',' in location else location
    
    # Try to extract additional data from JSON-LD or meta tags
    try:
        # Look for JSON-LD structured data (this is the primary data source for Luma)
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld and json_ld.string:
            data = json.loads(json_ld.string)
            if isinstance(data, dict):
                # Extract title
                if not title and data.get('name'):
                    title = data['name']
                
                # Extract datetime (include both start and end if available)
                if not datetime_str and data.get('startDate'):
                    datetime_str = data['startDate']
                    if data.get('endDate'):
                        # Include end time for better time representation
                        start_time = data['startDate'].split('T')[1].split('.')[0] if 'T' in data['startDate'] else ''
                        end_time = data['endDate'].split('T')[1].split('.')[0] if 'T' in data['endDate'] else ''
                        date_part = data['startDate'].split('T')[0] if 'T' in data['startDate'] else data['startDate']
                        if start_time and end_time:
                            # Format as readable time range
                            datetime_str = f"{date_part}T{start_time} - {end_time}"
                
                # Extract location
                if not location:
                    if data.get('location', {}).get('name'):
                        location = data['location']['name']
                    elif data.get('location', {}).get('address', {}).get('streetAddress'):
                        # Use street address if name not available
                        addr = data['location']['address']
                        location = addr.get('streetAddress', '')
                        if addr.get('addressLocality'):
                            location += f", {addr['addressLocality']}"
                        if addr.get('addressRegion'):
                            location += f", {addr['addressRegion']}"
                
                # Extract organizer from JSON-LD
                if not organizer and data.get('organizer'):
                    organizers = data.get('organizer', [])
                    if isinstance(organizers, list) and len(organizers) > 0:
                        organizer = organizers[0].get('name')
                    elif isinstance(organizers, dict):
                        organizer = organizers.get('name')
                
                # Extract description from JSON-LD (most reliable)
                if data.get('description'):
                    json_description = data['description']
                    # Use JSON-LD description if it's more substantial than what we found
                    if not description or len(json_description) > len(description):
                        description = json_description
                
                # Enhanced registration type detection BEFORE processing offers
                if not registration_type:
                    # First check page text for explicit closure messages
                    page_text = soup.get_text().lower()
                    if any(phrase in page_text for phrase in [
                        'registration closed', 
                        'registration is closed',
                        'this event is not currently taking registrations',
                        'registrations are closed',
                        'registration has closed'
                    ]):
                        registration_type = "Registration Closed"
                    elif any(phrase in page_text for phrase in [
                        'event is full', 
                        'fully booked', 
                        'sold out',
                        'no longer accepting'
                    ]):
                        registration_type = "Sold Out"
                    elif ('waitlist' in page_text and 
                          (any(event_phrase in page_text for event_phrase in [
                              'join the waitlist', 'join waitlist', 'event is full',
                              'capacity reached', 'waitlist to attend', 'event full'
                          ]) or
                           # Check for actual waitlist buttons (optimized)
                           any((btn_text := elem.get_text(strip=True).lower()) in ['join waitlist', 'join the waitlist'] 
                               for elem in soup.find_all(['button', 'a']))
                          ) and
                          not any(app_phrase in page_text for app_phrase in [
                              'join the waitlist for  the solution', 'waitlist for our', 'app waitlist',
                              'waitlist for the solution', 'product waitlist', 'service waitlist'
                          ])):
                        registration_type = "Waitlist"
                
                # Extract price and registration type from offers
                if data.get('offers'):
                    offers = data.get('offers', [])
                    if isinstance(offers, list) and len(offers) > 0:
                        offer = offers[0]
                        offer_price = offer.get('price', 0)
                        currency = offer.get('priceCurrency', 'USD').upper()
                        availability = offer.get('availability', '')
                        
                        # Set price
                        if offer_price == 0:
                            price = "Free"
                        else:
                            price = f"${offer_price}"
                            if currency != 'USD':
                                price = f"{offer_price} {currency}"
                        
                        # Set registration type based on availability (but don't override if already detected)
                        if not registration_type:
                            if 'OutOfStock' in availability or 'SoldOut' in availability:
                                registration_type = "Sold Out"
                            elif 'InStock' in availability:
                                # Default to one-click RSVP if in stock
                                registration_type = "One-Click RSVP"
                            else:
                                # Default registration type if availability unclear
                                registration_type = "One-Click RSVP"
    except Exception as e:
        print(f"  Error parsing JSON-LD: {e}")
    
    # Enhanced registration type detection for remaining cases (script data analysis)
    if not registration_type:
        # Check script tags for comprehensive event data
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                # Check for sold out / capacity flags first (most definitive)
                if 'sold_out' in script.string or 'is_sold_out' in script.string:
                    sold_out_match = re.search(r'"(sold_out|is_sold_out)":\s*true', script.string)
                    if sold_out_match:
                        registration_type = "Sold Out"
                        break
                
                # Check for registration closed flags
                if 'registration_closed' in script.string or 'is_closed' in script.string:
                    closed_match = re.search(r'"(registration_closed|is_closed)":\s*true', script.string)
                    if closed_match:
                        registration_type = "Registration Closed"
                        break
                
                # Check for registration enabled (false means closed)
                if 'registration_enabled' in script.string or 'can_register' in script.string:
                    enabled_match = re.search(r'"(registration_enabled|can_register)":\s*false', script.string)
                    if enabled_match:
                        registration_type = "Registration Closed"
                        break
                
                # Check for waitlist enabled flag
                if 'waitlist_enabled' in script.string:
                    waitlist_match = re.search(r'"waitlist_enabled":\s*(true|false)', script.string)
                    if waitlist_match and waitlist_match.group(1) == 'true':
                        registration_type = "Waitlist"
                        break
        
        # Enhanced UI element detection with more specific selectors
        if not registration_type:
            # Look for registration buttons and indicators
            registration_selectors = [
                'button[data-testid*="register"]',
                'button[data-testid*="rsvp"]', 
                'button[data-testid*="waitlist"]',
                'button[data-testid*="ticket"]',
                '.registration-button',
                '.rsvp-button',
                '.ticket-button',
                'a[href*="register"]',
                'a[href*="rsvp"]',
                'span[class*="sold"]',
                'span[class*="waitlist"]'
            ]
            
            for selector in registration_selectors:
                elements = soup.select(selector)
                for element in elements:
                    element_text = element.get_text(strip=True).lower()
                    # More comprehensive text analysis for registration type
                    if any(phrase in element_text for phrase in ['sold out', 'event is full', 'fully booked']):
                        registration_type = "Sold Out"
                        break
                    elif any(phrase in element_text for phrase in ['join waitlist', 'waitlist', 'join the waitlist']):
                        registration_type = "Waitlist"
                        break
                    elif any(phrase in element_text for phrase in ['one-click rsvp', 'rsvp', 'register', 'sign up']):
                        registration_type = "One-Click RSVP"
                        break
                
                if registration_type:
                    break
            
            # Fallback: Look in page content for registration type indicators
            if not registration_type:
                page_text = soup.get_text().lower()
                if any(phrase in page_text for phrase in ['event is full', 'fully booked', 'sold out']):
                    registration_type = "Sold Out"
                else:
                    # Default to one-click RSVP if no specific indicators found
                    registration_type = "One-Click RSVP"
    
    # Set default price if not found
    if not price:
        # Default to Free if no price information found
        price = "Free"
    
    # Fallback: Extract description from meta description tag if JSON-LD didn't work
    if not description or len(description) < 50:
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            meta_description = meta_desc.get('content')
            if len(meta_description) > len(description or ""):
                description = meta_description
    
    # Extract organizer from meta image URL as fallback
    if not organizer:
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image and og_image.get('content'):
            image_url = og_image.get('content')
            # Look for host_name parameter in the URL
            host_match = re.search(r'host_name=([^&]+)', image_url)
            if host_match:
                from urllib.parse import unquote
                organizer = unquote(host_match.group(1))
    
    # Apply Unicode decoding to all fields
    return {
        "url": decode_unicode_escapes(event_url),
        "title": decode_unicode_escapes(title or "N/A"),
        "datetime": decode_unicode_escapes(datetime_str or "N/A"),
        "location": decode_unicode_escapes(location or "N/A"),
        "venue_name": decode_unicode_escapes(venue_name or "N/A"),
        "organizer": decode_unicode_escapes(organizer or "N/A"),
        "price": decode_unicode_escapes(price or "N/A"),
        "registration_type": decode_unicode_escapes(registration_type or "N/A"),
        "event_type": decode_unicode_escapes(event_type or "N/A"),
        "tags": decode_unicode_escapes(tags or "N/A"),
        "description": decode_unicode_escapes(description or "N/A"),
        "scraped_at": datetime.now().isoformat()
    }

async def main():
    print("Starting Luma scraping for NYC Tech events...")
    results = await fetch_and_extract()
    
    print(f"\nFound {len(results)} events")
    for item in results:
        print("FOUND:", item["title"])
    
    # Save results to both CSV and JSON with organized folder structure
    if results:
        # Generate timestamp for folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create organized directory structure: scraped_data/luma/date
        base_dir = "scraped_data"
        luma_dir = os.path.join(base_dir, "luma")
        run_dir = os.path.join(luma_dir, timestamp)
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
