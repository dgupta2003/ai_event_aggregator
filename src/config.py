"""
Configuration management for the AI Events Aggregator

This module handles all configuration settings including:
- API keys and credentials
- City-specific settings
- Database configuration
- Application settings
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from dataclasses import dataclass, field
from datetime import datetime

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str = field(default_factory=lambda: os.getenv('DATABASE_URL', 'postgresql://localhost:5432/events_db'))
    host: str = field(default_factory=lambda: os.getenv('DB_HOST', 'localhost'))
    port: int = field(default_factory=lambda: int(os.getenv('DB_PORT', '5432')))
    name: str = field(default_factory=lambda: os.getenv('DB_NAME', 'events_db'))
    user: str = field(default_factory=lambda: os.getenv('DB_USER', 'postgres'))
    password: str = field(default_factory=lambda: os.getenv('DB_PASSWORD', ''))


@dataclass
class APIConfig:
    """API keys and configuration"""
    eventbrite_key: str = field(default_factory=lambda: os.getenv('EVENTBRITE_API_KEY', ''))
    meetup_key: str = field(default_factory=lambda: os.getenv('MEETUP_API_KEY', ''))
    openai_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    apify_key: str = field(default_factory=lambda: os.getenv('APIFY_API_KEY', ''))
    
    # API Rate Limits (requests per hour)
    eventbrite_rate_limit: int = 1000
    meetup_rate_limit: int = 200
    openai_rate_limit: int = 3000
    apify_rate_limit: int = 100


@dataclass
class CityConfig:
    """City-specific configuration"""
    name: str = field(default_factory=lambda: os.getenv('DEFAULT_CITY', 'New York City'))
    country: str = field(default_factory=lambda: os.getenv('DEFAULT_COUNTRY', 'US'))
    state: Optional[str] = field(default_factory=lambda: os.getenv('DEFAULT_STATE', 'NY'))
    timezone: str = field(default_factory=lambda: os.getenv('DEFAULT_TIMEZONE', 'America/New_York'))
    
    # Search parameters
    search_radius_miles: int = 50
    max_events_per_source: int = 1000
    target_month: str = field(default_factory=lambda: os.getenv('TARGET_MONTH', 'October 2025'))


@dataclass
class AppConfig:
    """General application configuration"""
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    debug: bool = field(default_factory=lambda: os.getenv('DEBUG', 'False').lower() == 'true')
    data_dir: str = field(default_factory=lambda: os.getenv('DATA_DIR', 'data'))
    logs_dir: str = field(default_factory=lambda: os.getenv('LOGS_DIR', 'logs'))
    
    # Processing settings
    batch_size: int = 100
    max_workers: int = 4
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    
    # Data retention
    cleanup_after_days: int = 60
    backup_after_days: int = 30


@dataclass
class AIConfig:
    """AI/ML configuration"""
    model: str = field(default_factory=lambda: os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'))
    max_tokens: int = field(default_factory=lambda: int(os.getenv('OPENAI_MAX_TOKENS', '150')))
    temperature: float = field(default_factory=lambda: float(os.getenv('OPENAI_TEMPERATURE', '0.1')))
    
    # Classification settings
    confidence_threshold: float = 0.7
    batch_classification_size: int = 50
    
    # Keywords for tech detection
    tech_keywords: list = field(default_factory=lambda: [
        'tech', 'technology', 'software', 'programming', 'coding', 'development',
        'ai', 'artificial intelligence', 'machine learning', 'data science',
        'python', 'javascript', 'react', 'node', 'java', 'c++', 'rust', 'go',
        'web dev', 'mobile app', 'frontend', 'backend', 'full stack',
        'devops', 'cloud', 'aws', 'azure', 'kubernetes', 'docker',
        'cybersecurity', 'security', 'blockchain', 'crypto', 'web3',
        'startup', 'entrepreneur', 'innovation', 'hackathon', 'meetup',
        'conference', 'workshop', 'bootcamp', 'training', 'networking'
    ])


class Config:
    """Main configuration class that combines all settings"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.city = CityConfig()
        self.app = AppConfig()
        self.ai = AIConfig()
    
    def validate(self) -> bool:
        """Validate that all required configuration is present"""
        required_api_keys = [
            ('EVENTBRITE_API_KEY', self.api.eventbrite_key),
            ('OPENAI_API_KEY', self.api.openai_key),
        ]
        
        missing_keys = []
        for key_name, key_value in required_api_keys:
            if not key_value:
                missing_keys.append(key_name)
        
        if missing_keys:
            print(f"Warning: Missing API keys: {', '.join(missing_keys)}")
            print("Some features may not work properly.")
            return False
        
        return True
    
    def get_city_config(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific city"""
        from .requirements.cities_config import get_city_config
        
        city_config = get_city_config(city_name)
        if city_config:
            return {
                'name': city_config.name,
                'display_name': city_config.display_name,
                'country': city_config.country,
                'state': city_config.state,
                'timezone': city_config.timezone,
                'coordinates': city_config.coordinates,
                'search_names': {
                    'eventbrite': city_config.eventbrite_names,
                    'meetup': city_config.meetup_names
                }
            }
        return None
    
    def get_data_paths(self, city_name: str = None) -> Dict[str, str]:
        """Get file paths for data storage"""
        base_dir = self.app.data_dir
        city_suffix = f"_{city_name}" if city_name else ""
        
        return {
            'raw_dir': f"{base_dir}/raw{city_suffix}",
            'processed_dir': f"{base_dir}/processed{city_suffix}",
            'logs_dir': self.app.logs_dir,
            'backup_dir': f"{base_dir}/backup{city_suffix}"
        }
    
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.app.log_level,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': f"{self.app.logs_dir}/aggregator.log",
            'max_bytes': 10 * 1024 * 1024,  # 10MB
            'backup_count': 5
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def validate_environment() -> bool:
    """Validate that the environment is properly set up"""
    config = get_config()
    
    # Check if data directories exist
    data_paths = config.get_data_paths()
    for path in data_paths.values():
        if not os.path.exists(path):
            print(f"Creating directory: {path}")
            os.makedirs(path, exist_ok=True)
    
    # Validate configuration
    return config.validate()


# Environment validation on import
if __name__ != "__main__":
    validate_environment()
