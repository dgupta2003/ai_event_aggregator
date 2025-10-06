"""
Web scraper for platforms without APIs (Luma, Partiful)

This module handles scraping event data from websites using Playwright.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import re
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

from .base_collector import BaseCollector, CollectionResult
try:
    from ..requirements.cities_config import get_city_config
except ImportError:
    from requirements.cities_config import get_city_config


class WebScraper(BaseCollector):
    """Base web scraper for platforms without APIs"""
    
    def __init__(self, source_name: str, base_url: str):
        super().__init__(
            source_name=source_name,
            rate_limit=100  # Conservative rate limit for scraping
        )
        self.base_url = base_url
        self.logger = logging.getLogger(f"scraper.{source_name}")
    
    async def collect_events(self, city: str, start_date: datetime, end_date: datetime) -> CollectionResult:
        """
        Collect events using web scraping
        
        Args:
            city: City name to search for events
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CollectionResult with collected data
        """
        self.logger.info(f"Starting {self.source_name} scraping for {city}")
        
        # Get city configuration
        city_config = get_city_config(city)
        if not city_config:
            return CollectionResult(
                success=False,
                data=[],
                errors=[f"City '{city}' not supported"],
                source=self.source_name,
                city=city,
                collected_at=datetime.now()
            )
        
        all_events = []
        errors = []
        
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                
                # Scrape events
                events = await self._scrape_events(context, city, start_date, end_date)
                all_events.extend(events)
                
                await browser.close()
        
        except Exception as e:
            error_msg = f"Error scraping {self.source_name} for {city}: {str(e)}"
            errors.append(error_msg)
            self.logger.error(error_msg)
        
        # Remove duplicates
        unique_events = self._deduplicate_events(all_events)
        
        # Save raw data
        filepath = self.save_raw_data(unique_events, city)
        
        result = CollectionResult(
            success=len(unique_events) > 0,
            data=unique_events,
            errors=errors,
            source=self.source_name,
            city=city,
            collected_at=datetime.now(),
            total_events=len(unique_events),
            api_calls_made=0  # No API calls for scraping
        )
        
        self.log_collection_stats(result)
        return result
    
    async def _scrape_events(self, context, city: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Scrape events from the website
        
        This method should be implemented by subclasses for specific platforms
        """
        raise NotImplementedError("Subclasses must implement _scrape_events")
    
    async def _navigate_to_search_page(self, page: Page, city: str) -> bool:
        """
        Navigate to the search page for a specific city
        
        This method should be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _navigate_to_search_page")
    
    async def _extract_events_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extract events from the current page
        
        This method should be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _extract_events_from_page")
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse various date formats to ISO format
        
        Args:
            date_str: Date string to parse
            
        Returns:
            ISO formatted date string or None
        """
        if not date_str:
            return None
        
        # Common date patterns
        date_patterns = [
            r'(\w{3})\s+(\d{1,2}),?\s+(\d{4})',  # "Oct 15, 2025"
            r'(\d{1,2})/(\d{1,2})/(\d{4})',      # "10/15/2025"
            r'(\d{4})-(\d{2})-(\d{2})',          # "2025-10-15"
        ]
        
        # Try to parse with common patterns
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if '/' in date_str:
                        month, day, year = match.groups()
                        dt = datetime(int(year), int(month), int(day))
                    elif '-' in date_str:
                        year, month, day = match.groups()
                        dt = datetime(int(year), int(month), int(day))
                    else:
                        # Handle "Oct 15, 2025" format
                        month_name, day, year = match.groups()
                        month_num = {
                            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                        }.get(month_name.lower()[:3])
                        if month_num:
                            dt = datetime(int(year), month_num, int(day))
                        else:
                            continue
                    
                    return dt.isoformat() + 'Z'
                except ValueError:
                    continue
        
        return None
    
    def _clean_event_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and validate scraped event data
        
        Args:
            event: Raw event data
            
        Returns:
            Cleaned event data
        """
        # Clean text fields
        for field in ['title', 'description', 'venue_name', 'city']:
            if field in event:
                event[field] = self.clean_text(event[field])
        
        # Ensure required fields
        if not event.get('title'):
            event['title'] = 'Untitled Event'
        
        if not event.get('url'):
            event['url'] = self.base_url
        
        # Parse and clean dates
        if event.get('start_time'):
            parsed_date = self._parse_date(event['start_time'])
            if parsed_date:
                event['start_time'] = parsed_date
        
        return event


class LumaScraper(WebScraper):
    """Scraper for Luma events"""
    
    def __init__(self):
        super().__init__(
            source_name="luma",
            base_url="https://lu.ma"
        )
    
    async def _scrape_events(self, context, city: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape events from Luma"""
        all_events = []
        
        try:
            page = await context.new_page()
            
            # Navigate to search page
            search_url = f"{self.base_url}/search?q={city}+tech"
            await page.goto(search_url, wait_until='networkidle')
            
            # Wait for events to load
            await page.wait_for_selector('.event-card, .event-item', timeout=10000)
            
            # Extract events from current page
            events = await self._extract_events_from_page(page)
            all_events.extend(events)
            
            # Handle pagination if needed
            try:
                next_button = await page.query_selector('a[aria-label="Next"], .next-page')
                if next_button:
                    await next_button.click()
                    await page.wait_for_load_state('networkidle')
                    
                    # Extract more events
                    more_events = await self._extract_events_from_page(page)
                    all_events.extend(more_events)
            except:
                pass  # No pagination or pagination failed
            
            await page.close()
            
        except Exception as e:
            self.logger.error(f"Error scraping Luma: {e}")
        
        return all_events
    
    async def _extract_events_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """Extract events from Luma page"""
        events = []
        
        try:
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find event elements (these selectors may need adjustment based on actual Luma HTML)
            event_elements = soup.find_all(['div', 'article'], class_=re.compile(r'event|card'))
            
            for element in event_elements:
                try:
                    # Extract event information
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|name'))
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # Skip if no title
                    if not title:
                        continue
                    
                    # Extract URL
                    link_elem = element.find('a', href=True)
                    url = urljoin(self.base_url, link_elem['href']) if link_elem else self.base_url
                    
                    # Extract date/time (this will need to be adjusted based on actual HTML structure)
                    date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time'))
                    start_time = date_elem.get_text(strip=True) if date_elem else ''
                    
                    # Extract venue/location
                    venue_elem = element.find(['span', 'div'], class_=re.compile(r'venue|location|address'))
                    venue_name = venue_elem.get_text(strip=True) if venue_elem else ''
                    
                    # Extract description
                    desc_elem = element.find(['p', 'div'], class_=re.compile(r'description|summary'))
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    # Create event object
                    event = {
                        'id': f"luma_{hash(url)}",
                        'source_id': str(hash(url)),
                        'source': 'luma',
                        'title': title,
                        'description': description,
                        'start_time': start_time,
                        'end_time': '',  # Luma might not have end times
                        'url': url,
                        'venue_name': venue_name,
                        'city': '',  # We'll need to extract this
                        'category': 'tech',
                        'tags': [],
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                    }
                    
                    # Clean and validate
                    event = self._clean_event_data(event)
                    if self.validate_event_data(event):
                        events.append(event)
                
                except Exception as e:
                    self.logger.warning(f"Error extracting Luma event: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error extracting Luma events: {e}")
        
        return events


class PartifulScraper(WebScraper):
    """Scraper for Partiful events"""
    
    def __init__(self):
        super().__init__(
            source_name="partiful",
            base_url="https://partiful.com"
        )
    
    async def _scrape_events(self, context, city: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Scrape events from Partiful"""
        all_events = []
        
        try:
            page = await context.new_page()
            
            # Navigate to search page (Partiful's search structure may be different)
            search_url = f"{self.base_url}/search?location={city}&category=tech"
            await page.goto(search_url, wait_until='networkidle')
            
            # Wait for events to load
            await page.wait_for_selector('.event, .party-card', timeout=10000)
            
            # Extract events from current page
            events = await self._extract_events_from_page(page)
            all_events.extend(events)
            
            await page.close()
            
        except Exception as e:
            self.logger.error(f"Error scraping Partiful: {e}")
        
        return all_events
    
    async def _extract_events_from_page(self, page: Page) -> List[Dict[str, Any]]:
        """Extract events from Partiful page"""
        events = []
        
        try:
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find event elements (these selectors may need adjustment)
            event_elements = soup.find_all(['div', 'article'], class_=re.compile(r'event|party|card'))
            
            for element in event_elements:
                try:
                    # Extract event information (similar to Luma but with Partiful-specific selectors)
                    title_elem = element.find(['h1', 'h2', 'h3'], class_=re.compile(r'title|name'))
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    if not title:
                        continue
                    
                    # Extract URL
                    link_elem = element.find('a', href=True)
                    url = urljoin(self.base_url, link_elem['href']) if link_elem else self.base_url
                    
                    # Extract other details (adjust selectors as needed)
                    date_elem = element.find(['time', 'span'], class_=re.compile(r'date|time'))
                    start_time = date_elem.get_text(strip=True) if date_elem else ''
                    
                    venue_elem = element.find(['span', 'div'], class_=re.compile(r'venue|location'))
                    venue_name = venue_elem.get_text(strip=True) if venue_elem else ''
                    
                    # Create event object
                    event = {
                        'id': f"partiful_{hash(url)}",
                        'source_id': str(hash(url)),
                        'source': 'partiful',
                        'title': title,
                        'description': '',
                        'start_time': start_time,
                        'end_time': '',
                        'url': url,
                        'venue_name': venue_name,
                        'city': '',
                        'category': 'tech',
                        'tags': [],
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                    }
                    
                    # Clean and validate
                    event = self._clean_event_data(event)
                    if self.validate_event_data(event):
                        events.append(event)
                
                except Exception as e:
                    self.logger.warning(f"Error extracting Partiful event: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error extracting Partiful events: {e}")
        
        return events


# Note: The actual selectors for Luma and Partiful will need to be determined
# by inspecting their HTML structure. The above code provides a framework
# that can be adjusted once we see the actual website structure.
