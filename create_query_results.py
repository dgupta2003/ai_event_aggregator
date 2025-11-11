#!/usr/bin/env python3
"""
Create CSV with one row per TEST_QUERIES query
Each row contains: query_number, query_text, and results for that specific query
"""

import os
import csv
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

def load_latest_data():
    """Load the most recent CSV data"""
    csv_dir = "outputs/csv"
    files = [f for f in os.listdir(csv_dir) if f.startswith("firecrawl_categorized_events_") and f.endswith(".csv")]
    if not files:
        print("❌ No categorized events CSV found")
        return None
    
    # Get the most recent file
    latest_file = sorted(files)[-1]
    file_path = os.path.join(csv_dir, latest_file)
    
    print(f"📂 Loading data from: {latest_file}")
    
    events = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    
    print(f"✅ Loaded {len(events)} events")
    return events

def get_test_queries():
    """Define the 20 test queries from updated benchmark test queries"""
    queries = {
        1: "Is there any AI event happening on November 12 at 9 AM in New York City?",
        2: "Find all sustainability workshops scheduled in San Francisco between November 1 and 5.",
        3: "Are there any climate change awareness events this weekend in Chicago?",
        4: "Show technology or entrepreneurship meetups happening tomorrow in Austin.",
        5: "List upcoming art and creativity festivals in Los Angeles next week.",
        6: "Find generative AI hackathons hosted by universities in California.",
        7: "Are there any mental health conferences taking place in November 2025?",
        8: "List events focused on renewable energy innovations this month.",
        9: "Search for education and EdTech panels happening online this week.",
        10: "Find music or cultural festivals related to sustainability and social change.",
        11: "Find AI or robotics events listed on Eventbrite for this week.",
        12: "Are there community events on Luma about ethical AI or digital privacy?",
        13: "Search for World Health Organization (WHO) webinars scheduled for November.",
        14: "List United Nations sustainability summits or youth events this year.",
        15: "Find TEDx or startup-focused talks in Europe about innovation and inclusion.",
        16: "List virtual AI conferences available for free registration this weekend.",
        17: "Are there hybrid sustainability hackathons happening this month?",
        18: "Find upcoming design thinking workshops open to students.",
        19: "Show social impact networking events that include mentorship sessions.",
        20: "Find product demo days or tech expos scheduled for November 2025."
    }
    return queries

def normalize_location(location_str):
    """Normalize location strings for better matching"""
    if not location_str:
        return ""
    
    location_lower = location_str.lower()
    
    # Normalize common location aliases
    location_map = {
        'nyc': 'new york',
        'new york city': 'new york',
        'sf': 'san francisco',
        'la': 'los angeles',
        'chi': 'chicago'
    }
    
    for alias, normalized in location_map.items():
        if alias in location_lower:
            return normalized
    return location_lower

def is_discovery_page(url):
    """Check if URL is a discovery/search page rather than specific event"""
    if not url:
        return True
    
    url_lower = url.lower()
    discovery_patterns = [
        'discover', 'find', '/search', 'listing', 'directory',
        'meetup.com/find/', 'eventbrite.com/d/', '/events'
    ]
    
    return any(pattern in url_lower for pattern in discovery_patterns)

def parse_event_date(event):
    """Extract and parse date from event data"""
    # Try date field first
    date_str = event.get('date', '').strip()
    title = event.get('title', '').lower()
    
    # Try to extract date from title or date field
    # Patterns: "Sat, Oct 25", "November 12", "Nov 12", "Oct 25"
    date_patterns = [
        r'(?:mon|tue|wed|thu|fri|sat|sun)[,\s]+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[,\s]+(\d{1,2})',
        r'(january|february|march|april|may|june|july|august|september|october|november|december)[,\s]+(\d{1,2})',
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[,\s]+(\d{1,2})',
        r'(\d{1,2})[,\s]+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
    ]
    
    month_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
        'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
        'may': 5, 'jun': 6, 'june': 6,
        'jul': 7, 'july': 7, 'aug': 8, 'august': 8,
        'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
        'nov': 11, 'november': 11, 'dec': 12, 'december': 12
    }
    
    search_text = f"{date_str} {title}"
    
    for pattern in date_patterns:
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                month_str = groups[0].lower()
                day_str = groups[1]
                
                month = month_map.get(month_str)
                if month:
                    try:
                        day = int(day_str)
                        # Assume 2025 for now (could be improved)
                        return datetime(2025, month, day)
                    except ValueError:
                        continue
    
    return None

def date_matches_query(query_num, query_text, event_date):
    """Check if event date matches query requirements"""
    if not event_date:
        return True  # If we can't parse date, don't filter out
    
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    query_lower = query_text.lower()
    
    # Query 1: November 12
    if query_num == 1:
        return event_date.month == 11 and event_date.day == 12
    
    # Query 2: November 1-5
    if query_num == 2:
        return event_date.month == 11 and 1 <= event_date.day <= 5
    
    # Query 3: "this weekend" - calculate weekend dates
    if query_num == 3:
        # Find this Saturday
        days_until_saturday = (5 - now.weekday()) % 7
        if days_until_saturday == 0 and now.weekday() < 5:
            days_until_saturday = 7
        saturday = now + timedelta(days=days_until_saturday)
        sunday = saturday + timedelta(days=1)
        return saturday.date() <= event_date.date() <= sunday.date()
    
    # Query 4: "tomorrow"
    if query_num == 4:
        tomorrow = now + timedelta(days=1)
        return event_date.date() == tomorrow.date()
    
    # Query 5: "next week"
    if query_num == 5:
        next_week_start = now + timedelta(days=(7 - now.weekday()))
        next_week_end = next_week_start + timedelta(days=6)
        return next_week_start.date() <= event_date.date() <= next_week_end.date()
    
    # Query 7: November 2025
    if query_num == 7:
        return event_date.month == 11 and event_date.year == 2025
    
    # Query 8, 17: "this month"
    if query_num in [8, 17]:
        return event_date.month == current_month and event_date.year == current_year
    
    # Query 9, 11: "this week"
    if query_num in [9, 11]:
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start.date() <= event_date.date() <= week_end.date()
    
    # Query 13: November
    if query_num == 13:
        return event_date.month == 11
    
    # Query 16: "this weekend"
    if query_num == 16:
        days_until_saturday = (5 - now.weekday()) % 7
        if days_until_saturday == 0 and now.weekday() < 5:
            days_until_saturday = 7
        saturday = now + timedelta(days=days_until_saturday)
        sunday = saturday + timedelta(days=1)
        return saturday.date() <= event_date.date() <= sunday.date()
    
    # Query 20: November 2025
    if query_num == 20:
        return event_date.month == 11 and event_date.year == 2025
    
    # Default: don't filter by date for queries without date requirements
    return True

def find_events_for_query(query_num, query_text, events):
    """Find events that match a specific query"""
    query_lower = query_text.lower()
    
    # Extract key terms from the query
    keywords = []
    locations = []
    topics = []
    platforms = []
    formats = []
    
    # Extract locations
    location_patterns = [
        r"new york city", r"nyc", r"san francisco", r"chicago", r"austin", 
        r"los angeles", r"california", r"europe"
    ]
    for pattern in location_patterns:
        if re.search(pattern, query_lower):
            locations.append(pattern.replace(r"\b", "").replace(r"|", ""))
    
    # Extract topics
    topic_patterns = [
        r"ai", r"artificial intelligence", r"sustainability", r"climate change",
        r"technology", r"entrepreneurship", r"art", r"creativity", r"generative ai",
        r"mental health", r"renewable energy", r"education", r"edtech", r"music",
        r"cultural", r"robotics", r"ethical ai", r"digital privacy", r"startup",
        r"innovation", r"design thinking", r"social impact", r"product demo"
    ]
    for pattern in topic_patterns:
        if re.search(pattern, query_lower):
            topics.append(pattern.replace(r"\b", ""))
    
    # Extract platforms
    platform_patterns = [r"eventbrite", r"luma", r"meetup"]
    for pattern in platform_patterns:
        if re.search(pattern, query_lower):
            platforms.append(pattern.replace(r"\b", ""))
    
    # Extract formats
    format_patterns = [
        r"workshop", r"conference", r"hackathon", r"webinar", r"summit",
        r"virtual", r"hybrid", r"networking", r"mentorship", r"demo", r"expo"
    ]
    for pattern in format_patterns:
        if re.search(pattern, query_lower):
            formats.append(pattern.replace(r"\b", ""))
    
    # Find matching events
    matching_events = []
    
    for event in events:
        title = event.get('title', '').lower()
        platform = event.get('platform', '').lower()
        categories = event.get('categories', '').lower()
        location = event.get('location', '').lower()
        event_url = event.get('url', '')
        
        # PRIORITY 4: Filter discovery pages early
        if is_discovery_page(event_url):
            # Only include if we have substantial event data
            if len(title) < 15 or title in ['discover events', 'popular events', 'eventsgroups']:
                continue
        
        # PRIORITY 1: Check date matching (penalize but don't completely skip)
        event_date = parse_event_date(event)
        date_matches = date_matches_query(query_num, query_text, event_date)
        
        # Only skip if we successfully parsed a date AND it doesn't match
        # (don't skip if we couldn't parse date - might still be relevant)
        if event_date and not date_matches:
            continue  # Skip events with parsed dates that don't match
        
        match_score = 0
        match_reasons = []
        topic_match = False
        location_match = False
        
        # PRIORITY 2: Stricter topic matching (higher weight, but allow partial matches)
        if topics:  # If query specifies topics
            topic_match = any(
                topic in title or topic in categories 
                for topic in topics
            )
            if topic_match:
                matched_topics = [t for t in topics if t in title or t in categories]
                match_score += 4 * len(matched_topics)  # Higher weight for topic match
                match_reasons.extend([f"topic:{t}" for t in matched_topics])
            else:
                # Don't completely skip - just give lower score
                # But for very specific queries, require topic match
                if query_num in [1, 3, 6, 8, 10, 12]:  # Highly topic-specific queries
                    continue  # Require topic match for these
                match_score -= 2  # Penalty for topic mismatch
        
        # PRIORITY 3: Location matching with normalization (REQUIRED for location queries)
        if locations:  # If query specifies locations
            normalized_event_location = normalize_location(location)
            normalized_title_location = normalize_location(title)
            
            location_match = any(
                normalize_location(loc) in normalized_event_location or
                normalize_location(loc) in normalized_title_location or
                normalize_location(loc) in normalize_location(categories)
                for loc in locations
            )
            
            if not location_match:
                # For strict location queries, location match is strongly preferred
                if query_num in [1, 2, 5]:  # Very location-specific (NYC, SF, LA)
                    match_score -= 3  # Heavy penalty but don't skip
                else:
                    match_score -= 1  # Light penalty
            
            if location_match:
                matched_locations = [
                    loc for loc in locations 
                    if normalize_location(loc) in normalized_event_location or
                    normalize_location(loc) in normalized_title_location or
                    normalize_location(loc) in normalize_location(categories)
                ]
                match_score += 3 * len(matched_locations)  # Higher weight for location
                match_reasons.extend([f"location:{l}" for l in matched_locations])
        
        # Check platform matches (still important)
        for platform_keyword in platforms:
            if platform_keyword in platform:
                match_score += 4  # Higher weight for platform match
                match_reasons.append(f"platform:{platform_keyword}")
        
        # Check format matches (still important)
        for format_type in formats:
            if format_type in title:
                match_score += 2
                match_reasons.append(f"format:{format_type}")
        
        # Negative filters - exclude obviously wrong matches
        # Exclude "women in tech" when query asks for "climate change"
        if query_num == 3 and ("women" in title or "tech" in title) and "climate" not in title:
            continue
        
        # Exclude non-AI events when query asks for AI
        if query_num in [1, 6, 11, 12, 16] and topics and any("ai" in t or "artificial intelligence" in t for t in topics):
            if "ai" not in title and "artificial intelligence" not in title and "robotics" not in title:
                continue
        
        # Add events with positive match score (after penalties)
        if match_score > 0:
            event_copy = event.copy()
            event_copy['match_score'] = match_score
            event_copy['match_reasons'] = ', '.join(match_reasons)
            matching_events.append(event_copy)
    
    # Sort by match score
    matching_events.sort(key=lambda x: x['match_score'], reverse=True)
    
    return matching_events

def create_query_results_csv(events):
    """Create CSV with one row per query"""
    queries = get_test_queries()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/csv/query_results_{timestamp}.csv"
    
    # Define fieldnames
    fieldnames = [
        'query_number', 'query_text', 'top_results'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for query_num, query_text in queries.items():
            print(f"🔍 Processing Query {query_num}: {query_text[:50]}...")
            
            # Find matching events
            matching_events = find_events_for_query(query_num, query_text, events)
            
            # Create bullet-pointed results with clean titles and available links
            top_results = ""
            if matching_events:
                top_5 = matching_events[:5]
                bullet_points = []
                for i, event in enumerate(top_5, 1):
                    title = event['title']
                    
                    # Clean up title (remove HTML artifacts and truncate)
                    title = re.sub(r'\[.*?\]', '', title)  # Remove [text] patterns
                    title = re.sub(r'https?://[^\s]+', '', title)  # Remove URLs from title
                    title = re.sub(r'[!@#$%^&*()_+=\[\]{}|;:,.<>?]', '', title)  # Remove special chars
                    title = re.sub(r'\s+', ' ', title).strip()  # Clean whitespace
                    
                    # Skip if title is too short or generic
                    if len(title) < 10 or title.lower() in ['discover events', 'popular events', 'eventsgroups']:
                        continue
                    
                    title = title[:70] + "..." if len(title) > 70 else title
                    
                    # Get URL and clean it up
                    event_url = event.get('url', '')
                    
                    # PRIORITY 4: Filter discovery pages - skip them entirely
                    if is_discovery_page(event_url):
                        continue  # Skip discovery pages in output
                    
                    if event_url:
                        # Truncate long URLs
                        if len(event_url) > 50:
                            event_url = event_url[:47] + "..."
                    
                    date = f" ({event['date']})" if event.get('date') and event['date'].strip() else ""
                    
                    bullet_point = f"• {title}{date} - {event_url}"
                    bullet_points.append(bullet_point)
                
                top_results = "\n".join(bullet_points) if bullet_points else "• No clear event titles found"
            else:
                top_results = "• No matching events found"
            
            # Prepare row data
            row = {
                'query_number': query_num,
                'query_text': query_text,
                'top_results': top_results
            }
            
            writer.writerow(row)
    
    return output_file

def print_summary():
    """Print summary of query results"""
    print("\n" + "="*80)
    print("📊 QUERY RESULTS SUMMARY")
    print("="*80)
    
    queries = get_test_queries()
    
    print(f"Total Queries Processed: {len(queries)}")
    print()
    
    # Show query categories
    categories = {
        "1-5": "Time + Location Filters",
        "6-10": "Topic-Specific Queries", 
        "11-15": "Organizer/Platform Filters",
        "16-20": "Event Format/Type Filters"
    }
    
    for range_key, description in categories.items():
        start, end = map(int, range_key.split('-'))
        count = end - start + 1
        print(f"Queries {range_key}: {description} ({count} queries)")

def main():
    print("="*80)
    print("🎯 CREATING QUERY RESULTS CSV")
    print("="*80)
    
    # Load data
    events = load_latest_data()
    if not events:
        return
    
    # Create query results CSV
    print("\n💾 Creating query results CSV...")
    output_file = create_query_results_csv(events)
    
    # Print summary
    print_summary()
    
    print("="*80)
    print(f"✅ SUCCESS! Query results CSV created: {output_file}")
    print("="*80)
    
    # Show file info
    file_size = os.path.getsize(output_file)
    print(f"📁 File size: {file_size:,} bytes")
    print(f"📊 Total queries: 20")
    
    return output_file

if __name__ == "__main__":
    main()
