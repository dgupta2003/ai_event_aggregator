"""
Data collection manager

This module coordinates all data collectors and manages the collection process.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from .base_collector import CollectionResult, setup_logging
from .eventbrite_collector import EventbriteCollector
from .meetup_collector import MeetupCollector
from .web_scraper import LumaScraper, PartifulScraper
try:
    from ..config import get_config
    from ..requirements.cities_config import get_supported_cities
except ImportError:
    from config import get_config
    from requirements.cities_config import get_supported_cities


class CollectorManager:
    """Manages all data collectors and coordinates collection process"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger("collector_manager")
        
        # Initialize collectors
        self.collectors = {}
        self._initialize_collectors()
        
        # Collection results storage
        self.collection_results: List[CollectionResult] = []
    
    def _initialize_collectors(self):
        """Initialize all available collectors"""
        try:
            # Eventbrite collector
            if self.config.api.eventbrite_key:
                self.collectors['eventbrite'] = EventbriteCollector(self.config.api.eventbrite_key)
                self.logger.info("Eventbrite collector initialized")
            else:
                self.logger.warning("Eventbrite API key not found")
            
            # Meetup collector
            if self.config.api.meetup_key:
                self.collectors['meetup'] = MeetupCollector(self.config.api.meetup_key)
                self.logger.info("Meetup collector initialized")
            else:
                self.logger.warning("Meetup API key not found")
            
            # Web scrapers (no API keys needed)
            self.collectors['luma'] = LumaScraper()
            self.collectors['partiful'] = PartifulScraper()
            self.logger.info("Web scrapers initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing collectors: {e}")
    
    def test_connections(self) -> Dict[str, bool]:
        """Test connections to all available data sources"""
        results = {}
        
        for name, collector in self.collectors.items():
            try:
                if hasattr(collector, 'test_connection'):
                    results[name] = collector.test_connection()
                else:
                    results[name] = True  # Web scrapers don't have connection tests
            except Exception as e:
                self.logger.error(f"Connection test failed for {name}: {e}")
                results[name] = False
        
        return results
    
    def collect_events_for_city(
        self, 
        city: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        sources: Optional[List[str]] = None
    ) -> List[CollectionResult]:
        """
        Collect events for a specific city from all available sources
        
        Args:
            city: City name to collect events for
            start_date: Start date for collection (defaults to now)
            end_date: End date for collection (defaults to 30 days from start)
            sources: List of sources to collect from (defaults to all available)
            
        Returns:
            List of CollectionResult objects
        """
        # Set default dates
        if start_date is None:
            start_date = datetime.now()
        if end_date is None:
            end_date = start_date + timedelta(days=30)
        
        # Use all sources if none specified
        if sources is None:
            sources = list(self.collectors.keys())
        
        self.logger.info(f"Starting collection for {city} from {', '.join(sources)}")
        self.logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
        
        results = []
        
        # Collect from each source
        for source_name in sources:
            if source_name not in self.collectors:
                self.logger.warning(f"Collector '{source_name}' not available")
                continue
            
            collector = self.collectors[source_name]
            
            try:
                self.logger.info(f"Collecting from {source_name}...")
                
                if source_name in ['luma', 'partiful']:
                    # Run async web scrapers
                    result = asyncio.run(collector.collect_events(city, start_date, end_date))
                else:
                    # Run sync API collectors
                    result = collector.collect_events(city, start_date, end_date)
                
                results.append(result)
                
                if result.success:
                    self.logger.info(f"✅ {source_name}: {result.total_events} events collected")
                else:
                    self.logger.warning(f"⚠️ {source_name}: Collection failed - {result.errors}")
                
            except Exception as e:
                self.logger.error(f"❌ {source_name}: Collection error - {e}")
                # Create failed result
                failed_result = CollectionResult(
                    success=False,
                    data=[],
                    errors=[str(e)],
                    source=source_name,
                    city=city,
                    collected_at=datetime.now()
                )
                results.append(failed_result)
        
        # Store results
        self.collection_results.extend(results)
        
        # Log summary
        total_events = sum(r.total_events for r in results if r.success)
        successful_sources = [r.source for r in results if r.success]
        failed_sources = [r.source for r in results if not r.success]
        
        self.logger.info(f"Collection complete: {total_events} total events from {len(successful_sources)} sources")
        if failed_sources:
            self.logger.warning(f"Failed sources: {', '.join(failed_sources)}")
        
        return results
    
    def collect_events_for_multiple_cities(
        self, 
        cities: List[str], 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        sources: Optional[List[str]] = None
    ) -> Dict[str, List[CollectionResult]]:
        """
        Collect events for multiple cities
        
        Args:
            cities: List of city names
            start_date: Start date for collection
            end_date: End date for collection
            sources: List of sources to collect from
            
        Returns:
            Dictionary mapping city names to collection results
        """
        all_results = {}
        
        for city in cities:
            self.logger.info(f"Collecting events for {city}...")
            city_results = self.collect_events_for_city(city, start_date, end_date, sources)
            all_results[city] = city_results
            
            # Add delay between cities to be respectful
            import time
            time.sleep(5)
        
        return all_results
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """Get summary of all collection results"""
        if not self.collection_results:
            return {"message": "No collections performed yet"}
        
        total_events = sum(r.total_events for r in self.collection_results if r.success)
        total_errors = sum(len(r.errors) for r in self.collection_results)
        
        # Group by source
        by_source = {}
        for result in self.collection_results:
            if result.source not in by_source:
                by_source[result.source] = {
                    'total_events': 0,
                    'successful_collections': 0,
                    'failed_collections': 0,
                    'cities': set()
                }
            
            by_source[result.source]['cities'].add(result.city)
            
            if result.success:
                by_source[result.source]['total_events'] += result.total_events
                by_source[result.source]['successful_collections'] += 1
            else:
                by_source[result.source]['failed_collections'] += 1
        
        # Convert sets to lists for JSON serialization
        for source_data in by_source.values():
            source_data['cities'] = list(source_data['cities'])
        
        return {
            'total_events': total_events,
            'total_errors': total_errors,
            'total_collections': len(self.collection_results),
            'by_source': by_source,
            'last_collection': max(r.collected_at for r in self.collection_results).isoformat() if self.collection_results else None
        }
    
    def save_collection_report(self, filepath: Optional[str] = None) -> str:
        """Save a detailed collection report"""
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"data/collection_report_{timestamp}.json"
        
        report = {
            'summary': self.get_collection_summary(),
            'detailed_results': [
                {
                    'source': r.source,
                    'city': r.city,
                    'success': r.success,
                    'total_events': r.total_events,
                    'api_calls_made': r.api_calls_made,
                    'errors': r.errors,
                    'collected_at': r.collected_at.isoformat()
                }
                for r in self.collection_results
            ]
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Collection report saved to {filepath}")
        return filepath
    
    def get_available_sources(self) -> List[str]:
        """Get list of available data sources"""
        return list(self.collectors.keys())
    
    def get_supported_cities(self) -> List[Dict[str, str]]:
        """Get list of supported cities"""
        return get_supported_cities()


def main():
    """Main function for running data collection"""
    # Set up logging
    setup_logging()
    
    # Initialize collector manager
    manager = CollectorManager()
    
    # Test connections
    print("Testing connections...")
    connection_results = manager.test_connections()
    for source, success in connection_results.items():
        status = "✅" if success else "❌"
        print(f"{status} {source}")
    
    # Get available sources and cities
    available_sources = manager.get_available_sources()
    supported_cities = manager.get_supported_cities()
    
    print(f"\nAvailable sources: {', '.join(available_sources)}")
    print(f"Supported cities: {', '.join([c['display_name'] for c in supported_cities])}")
    
    # Example collection (you can modify this)
    if available_sources:
        print("\nStarting data collection...")
        
        # Collect for New York City as an example
        results = manager.collect_events_for_city(
            city="New York City",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            sources=available_sources
        )
        
        # Print summary
        summary = manager.get_collection_summary()
        print(f"\nCollection Summary:")
        print(f"Total events: {summary['total_events']}")
        print(f"Sources used: {list(summary['by_source'].keys())}")
        
        # Save report
        report_path = manager.save_collection_report()
        print(f"Detailed report saved to: {report_path}")


if __name__ == "__main__":
    main()
