"""
Test script for data collectors

This script tests the data collection system without requiring API keys.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ingestion.base_collector import MockCollector
from ingestion.collector_manager import CollectorManager
from config import get_config


def test_mock_collector():
    """Test the mock collector"""
    print("🧪 Testing Mock Collector...")
    
    collector = MockCollector()
    
    # Test collection
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    result = collector.collect_events("New York City", start_date, end_date)
    
    print(f"✅ Mock collector result:")
    print(f"   Success: {result.success}")
    print(f"   Events collected: {result.total_events}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.data:
        print(f"   Sample event: {result.data[0]['title']}")
    
    return result.success


def test_collector_manager():
    """Test the collector manager"""
    print("\n🧪 Testing Collector Manager...")
    
    try:
        manager = CollectorManager()
        
        # Test getting available sources
        sources = manager.get_available_sources()
        print(f"✅ Available sources: {sources}")
        
        # Test getting supported cities
        cities = manager.get_supported_cities()
        print(f"✅ Supported cities: {[c['display_name'] for c in cities[:3]]}...")
        
        # Test collection summary (should be empty initially)
        summary = manager.get_collection_summary()
        print(f"✅ Collection summary: {summary['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Collector manager test failed: {e}")
        return False


def test_config():
    """Test configuration system"""
    print("\n🧪 Testing Configuration...")
    
    try:
        config = get_config()
        
        # Test basic config access
        print(f"✅ Default city: {config.city.name}")
        print(f"✅ Data directory: {config.app.data_dir}")
        print(f"✅ Log level: {config.app.log_level}")
        
        # Test city configuration
        try:
            city_config = config.get_city_config("New York City")
            if city_config:
                print(f"✅ NYC config found: {city_config['display_name']}")
            else:
                print("⚠️ NYC config not found")
        except Exception as e:
            print(f"⚠️ City config test skipped: {e}")
        
        # Test validation
        is_valid = config.validate()
        print(f"✅ Config validation: {'PASSED' if is_valid else 'FAILED (expected - no API keys)'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_data_directories():
    """Test that data directories are created"""
    print("\n🧪 Testing Data Directories...")
    
    try:
        config = get_config()
        data_paths = config.get_data_paths()
        
        for path_name, path in data_paths.items():
            if os.path.exists(path):
                print(f"✅ {path_name}: {path}")
            else:
                print(f"❌ {path_name}: {path} (not found)")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data directories test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🚀 Running Data Collection System Tests\n")
    
    tests = [
        ("Mock Collector", test_mock_collector),
        ("Configuration", test_config),
        ("Data Directories", test_data_directories),
        ("Collector Manager", test_collector_manager),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} {test_name}")
        if success:
            passed += 1
    
    print("=" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your data collection system is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
