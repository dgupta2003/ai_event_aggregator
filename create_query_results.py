#!/usr/bin/env python3
"""
Create CSV with one row per TEST_QUERIES query
Each row contains: query_number, query_text, and results for that specific query
"""

import os
import csv
import json
import re
from datetime import datetime
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
    """Define the 20 test queries from TEST_QUERIES (1).md"""
    queries = {
        1: "Is there any AI event happening on October 19 at 9 AM in New York City?",
        2: "Find all sustainability workshops scheduled in San Francisco between October 18 and 22.",
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
        13: "Search for World Health Organization (WHO) webinars scheduled for October.",
        14: "List United Nations sustainability summits or youth events this year.",
        15: "Find TEDx or startup-focused talks in Europe about innovation and inclusion.",
        16: "List virtual AI conferences available for free registration this weekend.",
        17: "Are there hybrid sustainability hackathons happening this month?",
        18: "Find upcoming design thinking workshops open to students.",
        19: "Show social impact networking events that include mentorship sessions.",
        20: "Find product demo days or tech expos scheduled for November 2025."
    }
    return queries

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
        
        match_score = 0
        match_reasons = []
        
        # Check topic matches
        for topic in topics:
            if topic in title or topic in categories:
                match_score += 2
                match_reasons.append(f"topic:{topic}")
        
        # Check location matches
        for loc in locations:
            if loc in title or loc in location or loc in categories:
                match_score += 2
                match_reasons.append(f"location:{loc}")
        
        # Check platform matches
        for platform_keyword in platforms:
            if platform_keyword in platform:
                match_score += 3
                match_reasons.append(f"platform:{platform_keyword}")
        
        # Check format matches
        for format_type in formats:
            if format_type in title:
                match_score += 2
                match_reasons.append(f"format:{format_type}")
        
        # Check specific query patterns
        if query_num == 1 and ("ai" in title or "artificial intelligence" in title) and ("october" in title or "19" in title):
            match_score += 3
            match_reasons.append("specific:ai_oct19")
        
        if query_num == 2 and ("sustainability" in title or "workshop" in title) and ("san francisco" in title or "sf" in title):
            match_score += 3
            match_reasons.append("specific:sustainability_workshop_sf")
        
        if query_num == 11 and "eventbrite" in platform and ("ai" in title or "robotics" in title):
            match_score += 3
            match_reasons.append("specific:eventbrite_ai")
        
        if query_num == 12 and "luma" in platform and ("ai" in title or "privacy" in title):
            match_score += 3
            match_reasons.append("specific:luma_ai_privacy")
        
        if query_num == 16 and ("virtual" in title or "conference" in title) and ("ai" in title):
            match_score += 3
            match_reasons.append("specific:virtual_ai_conference")
        
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
                    
                    # For discovery pages, show the platform instead
                    if 'discover' in event_url:
                        platform = event.get('platform', '').replace('_', ' ').title()
                        event_url = f"[{platform} Discovery Page]"
                    elif event_url:
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
