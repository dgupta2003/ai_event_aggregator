"""
LLM-Enhanced Web Scraper

This scraper uses multiple LLM APIs to extract event data from websites,
making it more robust than traditional CSS selector-based scraping.
"""

import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from playwright.async_api import async_playwright

from .base_collector import BaseCollector, CollectionResult
try:
    from ..processing.llm_manager import LLMManager
    from ..requirements.cities_config import get_city_config
except ImportError:
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.processing.llm_manager import LLMManager
    from src.requirements.cities_config import get_city_config

logger = logging.getLogger(__name__)


class LLMEnhancedScraper(BaseCollector):
    """Web scraper that uses LLMs for data extraction"""
    
    def __init__(self, source_name: str, base_url: str):
        super().__init__(
            source_name=source_name,
            rate_limit=50  # Conservative for LLM-based scraping
        )
        self.base_url = base_url
        self.llm_manager = LLMManager()
        self.logger = logging.getLogger(f"llm_scraper.{source_name}")
    
    async def collect_events(self, city: str, start_date: datetime, end_date: datetime) -> CollectionResult:
        """
        Collect events using LLM-based extraction
        
        Args:
            city: City name to search for events
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CollectionResult with collected data
        """
        self.logger.info(f"Starting LLM-enhanced scraping for {self.source_name} in {city}")
        
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
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                )
                
                # Scrape events using LLM
                events = await self._scrape_with_llm(context, city)
                all_events.extend(events)
                
                await browser.close()
        
        except Exception as e:
            error_msg = f"Error scraping {self.source_name} for {city}: {str(e)}"
            errors.append(error_msg)
            self.logger.error(error_msg)
        
        # Save raw data
        filepath = self.save_raw_data(all_events, city)
        
        result = CollectionResult(
            success=len(all_events) > 0,
            data=all_events,
            errors=errors,
            source=self.source_name,
            city=city,
            collected_at=datetime.now(),
            total_events=len(all_events),
            api_calls_made=0
        )
        
        self.log_collection_stats(result)
        return result
    
    async def _scrape_with_llm(self, context, city: str) -> List[Dict[str, Any]]:
        """
        Scrape events using LLM for extraction
        
        This method should be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _scrape_with_llm")


class LumaLLMScraper(LLMEnhancedScraper):
    """Luma scraper using LLM extraction"""
    
    def __init__(self):
        super().__init__(
            source_name="luma",
            base_url="https://lu.ma"
        )
    
    async def _scrape_with_llm(self, context, city: str) -> List[Dict[str, Any]]:
        """Scrape Luma events using LLM"""
        all_events = []
        
        try:
            page = await context.new_page()
            
            # Navigate to discover page
            discover_url = f"{self.base_url}/discover"
            self.logger.info(f"Navigating to {discover_url}")
            await page.goto(discover_url, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # Get page HTML
            html = await page.content()
            
            # Extract events using LLM
            self.logger.info("Extracting events using LLM...")
            extracted_events = self.llm_manager.extract_events_from_html(html, "luma")
            
            # Process and enrich each event
            for raw_event in extracted_events:
                try:
                    # Classify category using Claude
                    category = self.llm_manager.classify_event_category(
                        raw_event.get('title', ''),
                        raw_event.get('description', '')
                    )
                    
                    # Check tech relevance using Groq
                    tech_check = self.llm_manager.check_tech_relevance(
                        raw_event.get('title', ''),
                        raw_event.get('description', '')
                    )
                    
                    # Extract tags using GPT-4
                    tags = self.llm_manager.extract_tags(
                        raw_event.get('title', ''),
                        raw_event.get('description', '')
                    )
                    
                    # Build event object
                    event = {
                        'id': f"luma_{hash(raw_event.get('url', ''))}",
                        'source_id': str(hash(raw_event.get('url', ''))),
                        'source': 'luma',
                        'title': raw_event.get('title', ''),
                        'description': raw_event.get('description', ''),
                        'start_time': raw_event.get('start_time', datetime.now().isoformat()),
                        'end_time': raw_event.get('end_time', ''),
                        'url': raw_event.get('url', ''),
                        'venue_name': raw_event.get('venue_name', ''),
                        'city': city,
                        'category': category,
                        'tags': tags,
                        'is_tech_related': tech_check.get('is_tech_related', False),
                        'ai_confidence': tech_check.get('confidence', 0.0),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                    }
                    
                    all_events.append(event)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing event: {e}")
                    continue
            
            await page.close()
            
            self.logger.info(f"Extracted {len(all_events)} events using LLM")
            
        except Exception as e:
            self.logger.error(f"Error in LLM scraping: {e}")
        
        return all_events


class PartifulLLMScraper(LLMEnhancedScraper):
    """Partiful scraper using LLM extraction"""
    
    def __init__(self):
        super().__init__(
            source_name="partiful",
            base_url="https://partiful.com"
        )
    
    async def _scrape_with_llm(self, context, city: str) -> List[Dict[str, Any]]:
        """Scrape Partiful events using LLM"""
        all_events = []
        
        try:
            page = await context.new_page()
            
            # Try to navigate to search/discover page
            search_url = f"{self.base_url}/explore"  # Or /events, /discover
            self.logger.info(f"Navigating to {search_url}")
            await page.goto(search_url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # Get page HTML
            html = await page.content()
            
            # Extract events using LLM
            self.logger.info("Extracting Partiful events using LLM...")
            extracted_events = self.llm_manager.extract_events_from_html(html, "partiful")
            
            # Process each event
            for raw_event in extracted_events:
                try:
                    # Classify and enrich
                    category = self.llm_manager.classify_event_category(
                        raw_event.get('title', ''),
                        raw_event.get('description', '')
                    )
                    
                    tags = self.llm_manager.extract_tags(
                        raw_event.get('title', ''),
                        raw_event.get('description', '')
                    )
                    
                    tech_check = self.llm_manager.check_tech_relevance(
                        raw_event.get('title', ''),
                        raw_event.get('description', '')
                    )
                    
                    event = {
                        'id': f"partiful_{hash(raw_event.get('url', ''))}",
                        'source_id': str(hash(raw_event.get('url', ''))),
                        'source': 'partiful',
                        'title': raw_event.get('title', ''),
                        'description': raw_event.get('description', ''),
                        'start_time': raw_event.get('start_time', ''),
                        'end_time': raw_event.get('end_time', ''),
                        'url': raw_event.get('url', ''),
                        'venue_name': raw_event.get('venue_name', ''),
                        'city': city,
                        'category': category,
                        'tags': tags,
                        'is_tech_related': tech_check.get('is_tech_related', False),
                        'ai_confidence': tech_check.get('confidence', 0.0),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat(),
                    }
                    
                    all_events.append(event)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing Partiful event: {e}")
                    continue
            
            await page.close()
            
            self.logger.info(f"Extracted {len(all_events)} Partiful events using LLM")
            
        except Exception as e:
            self.logger.error(f"Error in Partiful LLM scraping: {e}")
        
        return all_events

