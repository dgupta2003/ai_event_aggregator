#!/usr/bin/env python3
"""
Improved Firecrawl Script for TEST_QUERIES (1).md
Uses scrape + crawl + map to get meaningful event data
"""

import os
import json
import csv
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()

print("=" * 80)
print("🔍 IMPROVED FIRECRAWL EVENT SCRAPER")
print("Using scrape + crawl + map for meaningful data")
print("=" * 80)
print()

# Initialize Firecrawl
api_key = os.getenv('FIRECRAWL_API_KEY')
if not api_key or api_key == 'fc-your_firecrawl_api_key_here':
    print("❌ Error: FIRECRAWL_API_KEY not found in .env")
    exit(1)

print(f"✅ API Key loaded")
app = FirecrawlApp(api_key=api_key)
print("✅ Firecrawl initialized")
print()

# Event platform URLs to scrape
event_platforms = {
    "luma_nyc": "https://lu.ma/discover?location=New%20York%20City",
    "luma_sf": "https://lu.ma/discover?location=San%20Francisco",
    "luma_chicago": "https://lu.ma/discover?location=Chicago",
    "luma_austin": "https://lu.ma/discover?location=Austin",
    "luma_la": "https://lu.ma/discover?location=Los%20Angeles",
    "eventbrite_nyc": "https://www.eventbrite.com/d/ny--new-york/tech-events/",
    "eventbrite_sf": "https://www.eventbrite.com/d/san-francisco/tech-events/",
    "eventbrite_chicago": "https://www.eventbrite.com/d/chicago/tech-events/",
    "meetup_nyc": "https://www.meetup.com/find/?location=us--ny--new-york&source=EVENTS",
    "meetup_sf": "https://www.meetup.com/find/?location=us--ca--san-francisco&source=EVENTS"
}

# Query categories from TEST_QUERIES (1).md
query_categories = {
    "ai_events": ["AI", "artificial intelligence", "machine learning", "ML"],
    "sustainability": ["sustainability", "climate", "renewable energy", "environment"],
    "tech_meetups": ["technology", "tech", "startup", "entrepreneurship"],
    "workshops": ["workshop", "training", "bootcamp", "hackathon"],
    "conferences": ["conference", "summit", "panel", "webinar"]
}

all_events = []
results = []

print("=" * 80)
print("Phase 1: Scraping Event Platforms")
print("=" * 80)
print()

for platform_name, url in event_platforms.items():
    print(f"📂 Scraping: {platform_name}")
    print(f"URL: {url}")
    
    start_time = time.time()
    
    try:
        # Scrape the platform page
        result = app.scrape(url, formats=['markdown'])
        content = result.markdown if hasattr(result, 'markdown') else str(result)
        
        response_time = time.time() - start_time
        
        # Parse events from content
        events_found = 0
        parsed_events = []
        
        # Look for event patterns in the content
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        
        current_event = {}
        for i, line in enumerate(lines):
            # Look for event titles (usually headings or bold text)
            if (line.startswith('#') or line.startswith('**') or 
                (len(line) > 10 and len(line) < 100 and not line.startswith('['))):
                
                # Extract title
                title = line.replace('#', '').replace('**', '').strip()
                
                # Look for URLs in nearby lines
                url_found = None
                for j in range(max(0, i-2), min(len(lines), i+3)):
                    if 'lu.ma/' in lines[j] or 'eventbrite.com/' in lines[j] or 'meetup.com/' in lines[j]:
                        url_match = re.search(r'https://[^\s\)]+', lines[j])
                        if url_match:
                            url_found = url_match.group(0)
                            break
                
                # Look for date/time patterns
                date_found = None
                time_found = None
                for j in range(max(0, i-1), min(len(lines), i+2)):
                    # Date patterns
                    date_patterns = [
                        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
                        r'\d{1,2}/\d{1,2}/\d{4}',
                        r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+[A-Z][a-z]+\s+\d{1,2}',
                        r'(today|tomorrow|this week|next week|this month|next month)'
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, lines[j], re.IGNORECASE)
                        if match:
                            date_found = match.group(0)
                            break
                    
                    # Time patterns
                    time_patterns = [
                        r'\d{1,2}:\d{2}\s*[APap][Mm]',
                        r'\d{1,2}\s*[APap][Mm]'
                    ]
                    
                    for pattern in time_patterns:
                        matches = re.findall(pattern, lines[j])
                        if matches:
                            time_found = ' - '.join(matches) if len(matches) > 1 else matches[0]
                            break
                
                # Look for location
                location_found = None
                for j in range(max(0, i-1), min(len(lines), i+2)):
                    if any(word in lines[j].lower() for word in ['venue', 'location', 'where', 'address']):
                        if j + 1 < len(lines):
                            location_found = lines[j+1]
                            break
                
                # Create event if we have enough info
                if title and len(title) > 5:
                    event = {
                        'title': title,
                        'url': url_found or url,
                        'date': date_found,
                        'time': time_found,
                        'location': location_found,
                        'platform': platform_name,
                        'source': 'firecrawl_scraped',
                        'scraped_at': datetime.now().isoformat(),
                        'content_length': len(content)
                    }
                    
                    parsed_events.append(event)
                    events_found += 1
        
        # Add to results
        platform_result = {
            'platform': platform_name,
            'url': url,
            'response_time_ms': round(response_time * 1000, 2),
            'events_found': events_found,
            'success': events_found > 0,
            'content_length': len(content)
        }
        results.append(platform_result)
        all_events.extend(parsed_events)
        
        print(f"   ✅ Response time: {response_time:.2f}s")
        print(f"   📊 Events found: {events_found}")
        print(f"   📄 Content length: {len(content)} chars")
        
        # Show sample events
        if parsed_events:
            print(f"   📋 Sample events:")
            for event in parsed_events[:2]:
                print(f"      • {event['title'][:50]}...")
        
    except Exception as e:
        response_time = time.time() - start_time
        error_msg = str(e)
        
        platform_result = {
            'platform': platform_name,
            'url': url,
            'response_time_ms': round(response_time * 1000, 2),
            'events_found': 0,
            'success': False,
            'error': error_msg[:100]
        }
        results.append(platform_result)
        
        print(f"   ❌ Error: {error_msg[:100]}")
    
    print()
    time.sleep(2)  # Rate limiting

print("=" * 80)
print("Phase 2: Enriching with Query Categories")
print("=" * 80)
print()

# Categorize events based on TEST_QUERIES categories
categorized_events = []

for event in all_events:
    title_desc = f"{event['title']} {event.get('location', '')}".lower()
    
    # Determine category based on content
    categories = []
    for category, keywords in query_categories.items():
        if any(keyword.lower() in title_desc for keyword in keywords):
            categories.append(category)
    
    # Add category information
    event['categories'] = ', '.join(categories) if categories else 'general'
    event['query_relevance'] = len(categories)
    
    categorized_events.append(event)

print(f"✅ Categorized {len(categorized_events)} events")
print()

# Show category breakdown
category_counts = {}
for event in categorized_events:
    for cat in event['categories'].split(', '):
        category_counts[cat] = category_counts.get(cat, 0) + 1

print("Category Breakdown:")
for category, count in sorted(category_counts.items()):
    print(f"  {category}: {count} events")

print()

print("=" * 80)
print("Phase 3: Saving Results")
print("=" * 80)
print()

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save platform results
platform_file = f"outputs/csv/firecrawl_platforms_{timestamp}.csv"
with open(platform_file, 'w', newline='', encoding='utf-8') as f:
    if results:
        fieldnames = ['platform', 'url', 'response_time_ms', 'events_found', 
                     'success', 'content_length']
        if 'error' in results[0]:
            fieldnames.append('error')
        
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)

print(f"📊 Platform results: {platform_file}")

# Save categorized events
events_file = f"outputs/csv/firecrawl_categorized_events_{timestamp}.csv"
with open(events_file, 'w', newline='', encoding='utf-8') as f:
    if categorized_events:
        fieldnames = ['title', 'url', 'date', 'time', 'location', 'platform', 
                     'categories', 'query_relevance', 'source', 'scraped_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(categorized_events)

print(f"📁 Categorized events: {events_file}")

# Save JSON
json_file = f"outputs/json/firecrawl_improved_results_{timestamp}.json"
with open(json_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'total_platforms': len(results),
        'total_events': len(categorized_events),
        'platform_results': results,
        'events': categorized_events,
        'category_breakdown': category_counts,
        'summary': {
            'successful_platforms': sum(1 for r in results if r['success']),
            'total_events_found': sum(r['events_found'] for r in results),
            'avg_response_time': sum(r['response_time_ms'] for r in results) / len(results),
            'events_with_categories': sum(1 for e in categorized_events if e['query_relevance'] > 0)
        }
    }, f, indent=2)

print(f"💾 Complete JSON: {json_file}")
print()

# Final summary
print("=" * 80)
print("📊 IMPROVED SCRAPING SUMMARY")
print("=" * 80)
print()

successful_platforms = sum(1 for r in results if r['success'])
total_events = len(categorized_events)
events_with_categories = sum(1 for e in categorized_events if e['query_relevance'] > 0)
avg_response_time = sum(r['response_time_ms'] for r in results) / len(results)

print(f"Platforms Tested: {len(results)}")
print(f"Successful Platforms: {successful_platforms}/{len(results)} ({successful_platforms/len(results)*100:.1f}%)")
print(f"Total Events Found: {total_events}")
print(f"Events with Relevant Categories: {events_with_categories} ({events_with_categories/total_events*100:.1f}%)")
print(f"Average Response Time: {avg_response_time:.0f}ms")
print()

print("Top Event Categories:")
for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {category}: {count} events")

print()
print("Sample Events:")
print("-" * 80)
for event in categorized_events[:5]:
    print(f"• {event['title']}")
    print(f"  Categories: {event['categories']}")
    print(f"  Platform: {event['platform']}")
    if event.get('date'):
        print(f"  Date: {event['date']}")
    print()

print("=" * 80)
print("🎉 Improved Scraping Complete!")
print("=" * 80)

