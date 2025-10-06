"""
Base classes and utilities for data collection

This module provides the foundation for all data collectors,
including common functionality like rate limiting, error handling,
and data validation.
"""

import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from ..config import get_config
except ImportError:
    from config import get_config


@dataclass
class CollectionResult:
    """Result of a data collection operation"""
    success: bool
    data: List[Dict[str, Any]]
    errors: List[str]
    source: str
    city: str
    collected_at: datetime
    total_events: int = 0
    api_calls_made: int = 0
    rate_limit_remaining: Optional[int] = None


class RateLimiter:
    """Simple rate limiter to respect API limits"""
    
    def __init__(self, requests_per_hour: int):
        self.requests_per_hour = requests_per_hour
        self.requests_made = 0
        self.reset_time = time.time() + 3600  # Reset every hour
    
    def can_make_request(self) -> bool:
        """Check if we can make another request"""
        current_time = time.time()
        
        # Reset counter if hour has passed
        if current_time >= self.reset_time:
            self.requests_made = 0
            self.reset_time = current_time + 3600
        
        return self.requests_made < self.requests_per_hour
    
    def wait_if_needed(self):
        """Wait if we've hit the rate limit"""
        if not self.can_make_request():
            wait_time = self.reset_time - time.time()
            if wait_time > 0:
                logging.info(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.requests_made = 0
                self.reset_time = time.time() + 3600
    
    def record_request(self):
        """Record that we made a request"""
        self.requests_made += 1


class BaseCollector(ABC):
    """Base class for all data collectors"""
    
    def __init__(self, source_name: str, api_key: str = None, rate_limit: int = 100):
        self.source_name = source_name
        self.api_key = api_key
        self.rate_limiter = RateLimiter(rate_limit)
        self.logger = logging.getLogger(f"collector.{source_name}")
        self.config = get_config()
        
        # Set up data directories
        self.raw_data_dir = Path(self.config.app.data_dir) / "raw"
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def collect_events(self, city: str, start_date: datetime, end_date: datetime) -> CollectionResult:
        """
        Collect events for a specific city and date range
        
        Args:
            city: City name to search for events
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            CollectionResult with collected data
        """
        pass
    
    def make_request(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """
        Make a rate-limited HTTP request
        
        Args:
            url: URL to request
            params: Query parameters
            headers: Request headers
            
        Returns:
            JSON response or None if failed
        """
        self.rate_limiter.wait_if_needed()
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                self.logger.warning(f"Rate limited by {self.source_name}. Waiting...")
                time.sleep(60)  # Wait 1 minute
                return self.make_request(url, params, headers)  # Retry
            else:
                self.logger.error(f"HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            return None
    
    def save_raw_data(self, data: List[Dict[str, Any]], city: str, timestamp: datetime = None) -> str:
        """
        Save raw collected data to file
        
        Args:
            data: Raw event data
            city: City name for file naming
            timestamp: Collection timestamp
            
        Returns:
            Path to saved file
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        filename = f"{self.source_name}_{city}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.raw_data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    'source': self.source_name,
                    'city': city,
                    'collected_at': timestamp.isoformat(),
                    'total_events': len(data),
                    'data': data
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(data)} events to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            return ""
    
    def load_raw_data(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load raw data from file
        
        Args:
            filepath: Path to data file
            
        Returns:
            Loaded data or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load data from {filepath}: {e}")
            return None
    
    def validate_event_data(self, event: Dict[str, Any]) -> bool:
        """
        Basic validation of event data
        
        Args:
            event: Event data to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['title', 'start_time', 'url']
        
        for field in required_fields:
            if field not in event or not event[field]:
                self.logger.warning(f"Missing required field '{field}' in event")
                return False
        
        # Validate date format
        try:
            datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            self.logger.warning(f"Invalid date format in event: {event.get('start_time')}")
            return False
        
        return True
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text data
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove HTML tags (basic)
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        return text.strip()
    
    def log_collection_stats(self, result: CollectionResult):
        """Log collection statistics"""
        self.logger.info(
            f"Collection complete: {result.total_events} events, "
            f"{result.api_calls_made} API calls, "
            f"{len(result.errors)} errors"
        )
        
        if result.errors:
            for error in result.errors:
                self.logger.warning(f"Collection error: {error}")


class MockCollector(BaseCollector):
    """Mock collector for testing without API calls"""
    
    def __init__(self, source_name: str = "mock"):
        super().__init__(source_name, rate_limit=1000)
    
    def collect_events(self, city: str, start_date: datetime, end_date: datetime) -> CollectionResult:
        """Generate mock event data for testing"""
        mock_events = [
            {
                'id': f"mock_{i}",
                'title': f"Mock Tech Event {i} in {city}",
                'description': f"This is a mock tech event in {city} for testing purposes.",
                'start_time': (start_date + timedelta(days=i)).isoformat(),
                'end_time': (start_date + timedelta(days=i, hours=2)).isoformat(),
                'url': f"https://mock.com/event/{i}",
                'venue_name': f"Mock Venue {i}",
                'city': city,
                'category': 'tech',
                'source': self.source_name
            }
            for i in range(5)  # Generate 5 mock events
        ]
        
        # Save mock data
        filepath = self.save_raw_data(mock_events, city)
        
        return CollectionResult(
            success=True,
            data=mock_events,
            errors=[],
            source=self.source_name,
            city=city,
            collected_at=datetime.now(),
            total_events=len(mock_events),
            api_calls_made=0
        )


def setup_logging():
    """Set up logging for data collection"""
    config = get_config()
    
    logging.basicConfig(
        level=getattr(logging, config.app.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.app.logs_dir + '/ingestion.log'),
            logging.StreamHandler()
        ]
    )
