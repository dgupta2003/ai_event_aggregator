"""
Firecrawl-based Event Collector

Uses Firecrawl API to scrape event data from various platforms with
structured extraction and intelligent parsing.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from firecrawl import FirecrawlApp

from .base_collector import BaseCollector, CollectionResult

logger = logging.getLogger(__name__)


class EventSchema(BaseModel):
    """Pydantic schema for structured event extraction"""
    title: str = Field(description="The event title or name")
    description: Optional[str] = Field(description="The event description or details")
    date: Optional[str] = Field(description="The event date and time")
    start_time: Optional[str] = Field(description="When the event starts")
    end_time: Optional[str] = Field(description="When the event ends")
    location: Optional[str] = Field(description="The event location or venue")
    venue: Optional[str] = Field(description="The venue name")
    address: Optional[str] = Field(description="The venue address")
    url: Optional[str] = Field(description="The event URL or link")
    price: Optional[str] = Field(description="The event price or cost")
    organizer: Optional[str] = Field(description="The event organizer or host")
    category: Optional[str] = Field(description="The event category or type")


class FirecrawlCollector(BaseCollector):
    """
    Event collector using Firecrawl API for intelligent web scraping
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Firecrawl collector
        
        Args:
            api_key: Firecrawl API key (defaults to FIRECRAWL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        super().__init__(source_name="firecrawl", api_key=self.api_key, rate_limit=100)
        
        if not self.api_key:
            raise ValueError(
                "Firecrawl API key not found. Set FIRECRAWL_API_KEY environment variable "
                "or pass api_key parameter"
            )
        
        self.app = FirecrawlApp(api_key=self.api_key)
        logger.info("Firecrawl collector initialized")
    
    def test_connection(self) -> bool:
        """
        Test Firecrawl API connection
        
        Returns:
            True if connection successful
        """
        try:
            # Try a simple scrape to test the API
            test_url = "https://lu.ma/discover"
            response = self.app.scrape(test_url, formats=['markdown'])
            logger.info("✅ Firecrawl API connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Firecrawl API connection failed: {str(e)}")
            return False
    
    def scrape_single_url(self, url: str, extract_schema: bool = True) -> Dict[str, Any]:
        """
        Scrape a single URL with optional structured extraction
        
        Args:
            url: URL to scrape
            extract_schema: Whether to use structured extraction
            
        Returns:
            Scraped data dictionary
        """
        try:
            if extract_schema:
                # Use structured extraction with schema
                response = self.app.extract(
                    urls=[url],
                    options={
                        'prompt': """Extract all event details including:
                        - Event title/name
                        - Full description
                        - Date and time (start and end if available)
                        - Location, venue, and address
                        - Event URL
                        - Price/cost information
                        - Organizer/host name
                        - Event category or type""",
                        'schema': EventSchema.model_json_schema()
                    }
                )
                return response
            else:
                # Simple scrape with JSON format
                response = self.app.scrape(url, formats=['json', 'markdown'])
                return response
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {}
    
    def crawl_events_page(
        self, 
        base_url: str, 
        limit: int = 50,
        include_paths: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl an events listing page and extract all events
        
        Args:
            base_url: Base URL to crawl (e.g., https://lu.ma/discover)
            limit: Maximum number of pages to crawl
            include_paths: Optional list of path patterns to include
            
        Returns:
            List of scraped event data
        """
        try:
            logger.info(f"Crawling {base_url} (limit: {limit})")
            
            crawl_options = {
                'limit': limit,
                'scrape_options': {
                    'formats': ['json', 'markdown']
                }
            }
            
            # Add path filters if provided
            if include_paths:
                crawl_options['include_paths'] = include_paths
            
            # Start the crawl
            crawl_result = self.app.crawl(base_url, **crawl_options)
            
            events = []
            if hasattr(crawl_result, 'data'):
                for doc in crawl_result.data:
                    events.append({
                        'url': doc.url if hasattr(doc, 'url') else None,
                        'markdown': doc.markdown if hasattr(doc, 'markdown') else None,
                        'json': doc.json if hasattr(doc, 'json') else None,
                        'metadata': doc.metadata if hasattr(doc, 'metadata') else {}
                    })
            
            logger.info(f"✅ Crawled {len(events)} pages from {base_url}")
            return events
            
        except Exception as e:
            logger.error(f"Error crawling {base_url}: {str(e)}")
            return []
    
    def batch_scrape_events(
        self, 
        urls: List[str], 
        extract_structured: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Batch scrape multiple event URLs
        
        Args:
            urls: List of event URLs to scrape
            extract_structured: Whether to use structured extraction
            
        Returns:
            List of scraped events
        """
        try:
            logger.info(f"Batch scraping {len(urls)} URLs")
            
            if extract_structured:
                # Use batch extraction with schema
                response = self.app.extract(
                    urls=urls,
                    options={
                        'prompt': """Extract event information including title, description, 
                        date/time, location, venue, price, organizer, and category.""",
                        'schema': EventSchema.model_json_schema()
                    }
                )
                return response.get('data', [])
            else:
                # Simple batch scrape
                batch_result = self.app.batch_scrape(urls, formats=['json'])
                events = []
                if hasattr(batch_result, 'data'):
                    for doc in batch_result.data:
                        events.append({
                            'url': doc.url if hasattr(doc, 'url') else None,
                            'json': doc.json if hasattr(doc, 'json') else None
                        })
                return events
                
        except Exception as e:
            logger.error(f"Error batch scraping: {str(e)}")
            return []
    
    def collect_luma_events(self, city: str = "New York") -> CollectionResult:
        """
        Collect events from Luma using Firecrawl
        
        Args:
            city: City name for location filtering
            
        Returns:
            CollectionResult with scraped events
        """
        logger.info(f"🔥 Collecting Luma events for {city} using Firecrawl")
        
        try:
            # Luma discover page
            base_url = "https://lu.ma/discover"
            
            # Crawl the discover page
            pages = self.crawl_events_page(
                base_url=base_url,
                limit=20,
                include_paths=['/[a-z0-9]{8}']  # Match Luma event URLs
            )
            
            # Extract event URLs
            event_urls = []
            for page in pages:
                url = page.get('url', '')
                # Filter for actual event pages (8-char alphanumeric IDs)
                if url and len(url.split('/')[-1]) == 8:
                    event_urls.append(url)
            
            logger.info(f"Found {len(event_urls)} event URLs")
            
            # Batch scrape the event pages
            events = []
            if event_urls:
                scraped = self.batch_scrape_events(event_urls[:10], extract_structured=True)
                events = scraped
            
            # Save raw data
            raw_data = {
                'source': 'luma_firecrawl',
                'city': city,
                'collected_at': datetime.now().isoformat(),
                'total_events': len(events),
                'events': events
            }
            
            filename = self.save_raw_data(raw_data, city)
            
            return CollectionResult(
                success=True,
                data=events,
                errors=[],
                source=self.source_name,
                city=city,
                collected_at=datetime.now(),
                total_events=len(events)
            )
            
        except Exception as e:
            logger.error(f"Error collecting Luma events: {str(e)}")
            return CollectionResult(
                success=False,
                data=[],
                errors=[str(e)],
                source=self.source_name,
                city=city,
                collected_at=datetime.now(),
                total_events=0
            )
    
    def collect_eventbrite_events(self, city: str = "New York") -> CollectionResult:
        """
        Collect events from Eventbrite using Firecrawl
        
        Args:
            city: City name for location filtering
            
        Returns:
            CollectionResult with scraped events
        """
        logger.info(f"🔥 Collecting Eventbrite events for {city} using Firecrawl")
        
        try:
            # Eventbrite search URL
            city_slug = city.lower().replace(' ', '-')
            base_url = f"https://www.eventbrite.com/d/{city_slug}/tech-events/"
            
            # Crawl the events page
            pages = self.crawl_events_page(
                base_url=base_url,
                limit=15
            )
            
            logger.info(f"Crawled {len(pages)} pages from Eventbrite")
            
            # Extract events from crawled pages
            events = []
            for page in pages:
                json_data = page.get('json', {})
                if json_data:
                    events.append(json_data)
            
            # Save raw data
            raw_data = {
                'source': 'eventbrite_firecrawl',
                'city': city,
                'collected_at': datetime.now().isoformat(),
                'total_events': len(events),
                'events': events
            }
            
            filename = self.save_raw_data(raw_data, city)
            
            return CollectionResult(
                success=True,
                data=events,
                errors=[],
                source=self.source_name,
                city=city,
                collected_at=datetime.now(),
                total_events=len(events)
            )
            
        except Exception as e:
            logger.error(f"Error collecting Eventbrite events: {str(e)}")
            return CollectionResult(
                success=False,
                data=[],
                errors=[str(e)],
                source=self.source_name,
                city=city,
                collected_at=datetime.now(),
                total_events=0
            )
    
    def collect_events(self, city: str = "New York", platform: str = "luma") -> CollectionResult:
        """
        Main method to collect events from specified platform
        
        Args:
            city: City name for location filtering
            platform: Platform to scrape ('luma', 'eventbrite', or 'custom')
            
        Returns:
            CollectionResult with scraped events
        """
        if platform.lower() == 'luma':
            return self.collect_luma_events(city)
        elif platform.lower() == 'eventbrite':
            return self.collect_eventbrite_events(city)
        else:
            return CollectionResult(
                success=False,
                data=[],
                errors=[f"Unknown platform: {platform}"],
                source=self.source_name,
                city=city,
                collected_at=datetime.now(),
                total_events=0
            )


if __name__ == "__main__":
    # Quick test
    logging.basicConfig(level=logging.INFO)
    
    collector = FirecrawlCollector()
    
    if collector.test_connection():
        result = collector.collect_luma_events("New York")
        print(f"\n{result}")

