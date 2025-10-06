#!/usr/bin/env python3
"""
Main data collection script

This script collects events from all available sources for a specified city.
Usage: python fetch_all.py [city] [days]
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ingestion.collector_manager import CollectorManager
from ingestion.base_collector import setup_logging
from config import get_config


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Collect tech events from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_all.py                    # Collect for default city (NYC) for next 30 days
  python fetch_all.py "San Francisco"    # Collect for San Francisco
  python fetch_all.py "London" 14        # Collect for London for next 14 days
  python fetch_all.py --test             # Run tests without collecting data
  python fetch_all.py --sources eventbrite meetup  # Only collect from specific sources
        """
    )
    
    parser.add_argument(
        'city',
        nargs='?',
        help='City name to collect events for (default: New York City)'
    )
    
    parser.add_argument(
        'days',
        nargs='?',
        type=int,
        help='Number of days to collect events for (default: 30)'
    )
    
    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['eventbrite', 'meetup', 'luma', 'partiful'],
        help='Specific sources to collect from (default: all available)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run tests instead of collecting data'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be collected without actually collecting'
    )
    
    return parser.parse_args()


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🤖 AI-Powered Tech Events Aggregator")
    print("📅 Data Collection System")
    print("=" * 60)


def print_collection_plan(city: str, days: int, sources: list):
    """Print collection plan"""
    print(f"\n📋 Collection Plan:")
    print(f"   City: {city}")
    print(f"   Date Range: {datetime.now().date()} to {(datetime.now() + timedelta(days=days)).date()}")
    print(f"   Sources: {', '.join(sources)}")
    print(f"   Total Days: {days}")


def print_results_summary(results: list):
    """Print collection results summary"""
    print(f"\n📊 Collection Results:")
    print("-" * 40)
    
    total_events = 0
    successful_sources = 0
    failed_sources = 0
    
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.source:12} {result.total_events:4} events")
        
        if result.success:
            total_events += result.total_events
            successful_sources += 1
        else:
            failed_sources += 1
            
        if result.errors:
            for error in result.errors[:2]:  # Show first 2 errors
                print(f"    ⚠️ {error}")
    
    print("-" * 40)
    print(f"Total Events: {total_events}")
    print(f"Successful Sources: {successful_sources}")
    print(f"Failed Sources: {failed_sources}")


def run_tests():
    """Run system tests"""
    print("\n🧪 Running System Tests...")
    
    # Import and run tests
    from ingestion.test_collectors import run_all_tests
    return run_all_tests()


def main():
    """Main function"""
    args = parse_arguments()
    
    # Print banner
    print_banner()
    
    # Set up logging
    if args.verbose:
        setup_logging()
    
    # Handle test mode
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Initialize collector manager
    print("\n🔧 Initializing collectors...")
    manager = CollectorManager()
    
    # Get available sources
    available_sources = manager.get_available_sources()
    if not available_sources:
        print("❌ No data sources available. Check your configuration.")
        sys.exit(1)
    
    # Determine sources to use
    if args.sources:
        sources = [s for s in args.sources if s in available_sources]
        if not sources:
            print(f"❌ None of the specified sources are available.")
            print(f"Available sources: {', '.join(available_sources)}")
            sys.exit(1)
    else:
        sources = available_sources
    
    # Get city configuration
    config = get_config()
    city = args.city or config.city.name
    
    # Validate city
    from requirements.cities_config import validate_city
    if not validate_city(city):
        print(f"❌ City '{city}' is not supported.")
        supported_cities = [c['display_name'] for c in manager.get_supported_cities()]
        print(f"Supported cities: {', '.join(supported_cities)}")
        sys.exit(1)
    
    # Set date range
    days = args.days or 30
    start_date = datetime.now()
    end_date = start_date + timedelta(days=days)
    
    # Print collection plan
    print_collection_plan(city, days, sources)
    
    # Handle dry run
    if args.dry_run:
        print("\n🔍 Dry run mode - no data will be collected")
        return
    
    # Test connections
    print(f"\n🔌 Testing connections to {len(sources)} sources...")
    connection_results = manager.test_connections()
    
    for source in sources:
        if source in connection_results:
            status = "✅" if connection_results[source] else "❌"
            print(f"{status} {source}")
        else:
            print(f"❓ {source} (connection test not available)")
    
    # Start collection
    print(f"\n🚀 Starting data collection...")
    print(f"This may take a few minutes depending on the number of events...")
    
    try:
        # Collect events
        results = manager.collect_events_for_city(
            city=city,
            start_date=start_date,
            end_date=end_date,
            sources=sources
        )
        
        # Print results
        print_results_summary(results)
        
        # Save detailed report
        report_path = manager.save_collection_report()
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Get summary statistics
        summary = manager.get_collection_summary()
        print(f"\n📈 Collection Summary:")
        print(f"   Total Events Collected: {summary['total_events']}")
        print(f"   Sources Used: {', '.join(summary['by_source'].keys())}")
        
        if summary['total_events'] > 0:
            print(f"\n🎉 Data collection completed successfully!")
            print(f"Raw data saved to: data/raw/")
        else:
            print(f"\n⚠️ No events were collected. Check your configuration and try again.")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Collection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
