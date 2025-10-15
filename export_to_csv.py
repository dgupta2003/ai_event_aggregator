#!/usr/bin/env python3
"""
Export processed events to CSV

This script processes raw event data and exports it to CSV format.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.processing import ProcessorManager

def export_events_to_csv(include_past=True, min_quality=0.1):
    """Export processed events to CSV"""
    
    print("\n🚀 Processing and exporting events to CSV...\n")
    
    # Initialize processor
    processor = ProcessorManager()
    
    # Process pipeline with relaxed settings to get all events
    processed_events = processor.process_pipeline(
        city=None,  # All cities
        include_past=include_past,
        min_quality=min_quality,
        save_output=False  # We'll export to CSV instead
    )
    
    if not processed_events:
        print("⚠️  No events to export")
        return None
    
    # Convert to list of dicts for pandas
    events_data = []
    for event in processed_events:
        events_data.append({
            'id': event.unified_id,
            'source': event.source.value,
            'title': event.title,
            'description': event.description[:200] if event.description else '',  # Truncate
            'start_time': event.start_time.strftime('%Y-%m-%d %H:%M') if event.start_time else '',
            'end_time': event.end_time.strftime('%Y-%m-%d %H:%M') if event.end_time else '',
            'url': event.url,
            'venue_name': event.location.venue_name or '',
            'city': event.location.city or '',
            'state': event.location.state or '',
            'latitude': event.location.latitude or '',
            'longitude': event.location.longitude or '',
            'is_online': event.location.is_online,
            'organizer': event.organizer.name or '',
            'category': event.category or '',
            'tags': ', '.join(event.tags[:5]) if event.tags else '',  # First 5 tags
            'is_tech_related': event.is_tech_related,
            'quality_score': round(event.quality_score, 2),
            'status': event.status.value,
            'capacity': event.capacity or '',
            'is_free': event.is_free,
            'price': event.price or '',
        })
    
    # Create DataFrame
    df = pd.DataFrame(events_data)
    
    # Export to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'events_export_{timestamp}.csv'
    df.to_csv(csv_filename, index=False)
    
    print(f"\n✅ Exported {len(df)} events to: {csv_filename}")
    print(f"\n📊 Summary:")
    print(f"   Total events: {len(df)}")
    print(f"   Sources: {df['source'].value_counts().to_dict()}")
    print(f"   Tech-related: {df['is_tech_related'].sum()}")
    print(f"   Cities: {df['city'].value_counts().head(3).to_dict()}")
    
    # Also save as Excel for easier viewing
    excel_filename = f'events_export_{timestamp}.xlsx'
    df.to_excel(excel_filename, index=False, engine='openpyxl')
    print(f"\n📑 Also saved as Excel: {excel_filename}")
    
    # Print sample
    print(f"\n📝 Sample events (first 3):")
    print("-" * 80)
    for i, row in df.head(3).iterrows():
        print(f"\n{i+1}. {row['title']}")
        print(f"   Source: {row['source']} | Date: {row['start_time']}")
        print(f"   Venue: {row['venue_name'] or 'N/A'} | City: {row['city'] or 'N/A'}")
        print(f"   Quality: {row['quality_score']} | Tech: {row['is_tech_related']}")
        print(f"   URL: {row['url']}")
    
    return csv_filename

if __name__ == "__main__":
    try:
        csv_file = export_events_to_csv(
            include_past=True,  # Include past events for demo
            min_quality=0.1  # Low threshold to get more events
        )
        
        if csv_file:
            print(f"\n🎉 Success! Open '{csv_file}' to view the data")
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        import traceback
        traceback.print_exc()

