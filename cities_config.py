"""
City Configuration for Multi-City Support

This module defines supported cities and their platform-specific identifiers.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import pytz


@dataclass
class CityConfig:
    """Configuration for a supported city"""
    name: str
    display_name: str
    country: str
    state: Optional[str]
    timezone: str
    alternative_names: List[str]
    eventbrite_names: List[str]
    meetup_names: List[str]
    coordinates: Dict[str, float]  # {"lat": 40.7128, "lng": -74.0060}


# Supported Cities Configuration
SUPPORTED_CITIES = {
    "new_york": CityConfig(
        name="new_york",
        display_name="New York City",
        country="US",
        state="NY",
        timezone="America/New_York",
        alternative_names=["NYC", "New York", "Manhattan", "Brooklyn"],
        eventbrite_names=["New York", "New York City", "NYC", "Manhattan", "Brooklyn"],
        meetup_names=["New York", "New York City", "NYC"],
        coordinates={"lat": 40.7128, "lng": -74.0060}
    ),
    "san_francisco": CityConfig(
        name="san_francisco",
        display_name="San Francisco",
        country="US",
        state="CA",
        timezone="America/Los_Angeles",
        alternative_names=["SF", "San Francisco", "Bay Area"],
        eventbrite_names=["San Francisco", "SF", "Bay Area"],
        meetup_names=["San Francisco", "SF"],
        coordinates={"lat": 37.7749, "lng": -122.4194}
    ),
    "london": CityConfig(
        name="london",
        display_name="London",
        country="GB",
        state=None,
        timezone="Europe/London",
        alternative_names=["London", "Greater London"],
        eventbrite_names=["London", "Greater London"],
        meetup_names=["London"],
        coordinates={"lat": 51.5074, "lng": -0.1278}
    ),
    "toronto": CityConfig(
        name="toronto",
        display_name="Toronto",
        country="CA",
        state="ON",
        timezone="America/Toronto",
        alternative_names=["Toronto", "GTA", "Greater Toronto"],
        eventbrite_names=["Toronto", "GTA"],
        meetup_names=["Toronto"],
        coordinates={"lat": 43.6532, "lng": -79.3832}
    ),
    "los_angeles": CityConfig(
        name="los_angeles",
        display_name="Los Angeles",
        country="US",
        state="CA",
        timezone="America/Los_Angeles",
        alternative_names=["LA", "Los Angeles", "LAX"],
        eventbrite_names=["Los Angeles", "LA"],
        meetup_names=["Los Angeles", "LA"],
        coordinates={"lat": 34.0522, "lng": -118.2437}
    ),
    "chicago": CityConfig(
        name="chicago",
        display_name="Chicago",
        country="US",
        state="IL",
        timezone="America/Chicago",
        alternative_names=["Chicago", "Windy City"],
        eventbrite_names=["Chicago"],
        meetup_names=["Chicago"],
        coordinates={"lat": 41.8781, "lng": -87.6298}
    ),
    "boston": CityConfig(
        name="boston",
        display_name="Boston",
        country="US",
        state="MA",
        timezone="America/New_York",
        alternative_names=["Boston", "Beantown"],
        eventbrite_names=["Boston"],
        meetup_names=["Boston"],
        coordinates={"lat": 42.3601, "lng": -71.0589}
    ),
    "seattle": CityConfig(
        name="seattle",
        display_name="Seattle",
        country="US",
        state="WA",
        timezone="America/Los_Angeles",
        alternative_names=["Seattle", "Emerald City"],
        eventbrite_names=["Seattle"],
        meetup_names=["Seattle"],
        coordinates={"lat": 47.6062, "lng": -122.3321}
    ),
    "austin": CityConfig(
        name="austin",
        display_name="Austin",
        country="US",
        state="TX",
        timezone="America/Chicago",
        alternative_names=["Austin", "ATX"],
        eventbrite_names=["Austin"],
        meetup_names=["Austin"],
        coordinates={"lat": 30.2672, "lng": -97.7431}
    )
}


def get_city_config(city_name: str) -> Optional[CityConfig]:
    """
    Get city configuration by name (supports various formats)
    
    Args:
        city_name: City name in any supported format
        
    Returns:
        CityConfig object or None if not found
    """
    city_name_lower = city_name.lower().strip()
    
    # Direct lookup
    if city_name_lower in SUPPORTED_CITIES:
        return SUPPORTED_CITIES[city_name_lower]
    
    # Search by display name and alternative names
    for city_key, config in SUPPORTED_CITIES.items():
        if (city_name_lower == config.display_name.lower() or
            city_name_lower in [alt.lower() for alt in config.alternative_names]):
            return config
    
    return None


def get_supported_cities() -> List[Dict[str, str]]:
    """
    Get list of all supported cities
    
    Returns:
        List of city info dictionaries
    """
    return [
        {
            "key": key,
            "display_name": config.display_name,
            "country": config.country,
            "state": config.state
        }
        for key, config in SUPPORTED_CITIES.items()
    ]


def validate_city(city_name: str) -> bool:
    """
    Check if a city is supported
    
    Args:
        city_name: City name to validate
        
    Returns:
        True if city is supported, False otherwise
    """
    return get_city_config(city_name) is not None


# Tech-related categories and keywords for AI filtering
TECH_CATEGORIES = [
    "Technology",
    "Science & Technology", 
    "Computers & Internet",
    "Software Development",
    "Artificial Intelligence",
    "Data Science",
    "Machine Learning",
    "Web Development",
    "Mobile Development",
    "DevOps",
    "Cybersecurity",
    "Blockchain",
    "Startup",
    "Entrepreneurship",
    "Innovation"
]

TECH_KEYWORDS = [
    "tech", "technology", "software", "programming", "coding", "development",
    "ai", "artificial intelligence", "machine learning", "data science",
    "python", "javascript", "react", "node", "java", "c++", "rust", "go",
    "web dev", "mobile app", "frontend", "backend", "full stack",
    "devops", "cloud", "aws", "azure", "kubernetes", "docker",
    "cybersecurity", "security", "blockchain", "crypto", "web3",
    "startup", "entrepreneur", "innovation", "hackathon", "meetup",
    "conference", "workshop", "bootcamp", "training", "networking"
]

def is_tech_related(text: str, categories: List[str] = None) -> bool:
    """
    Quick keyword-based tech relevance check
    
    Args:
        text: Text to analyze (title, description, categories)
        categories: Optional list of categories
        
    Returns:
        True if likely tech-related, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check categories first
    if categories:
        for category in categories:
            if any(keyword in category.lower() for keyword in TECH_KEYWORDS):
                return True
    
    # Check text content
    return any(keyword in text_lower for keyword in TECH_KEYWORDS)
