#!/usr/bin/env python3
"""
LLM Comparison Test Runner

Runs all test queries from TEST_QUERIES.md and compares performance
across GPT-4, Claude, Gemini, and Groq.
"""

import json
import time
from datetime import datetime
from src.processing.llm_manager import LLMManager, LLMProvider

# Test Queries
QUERIES = {
    "Set 1: Event Extraction": [
        {
            "id": "1.1",
            "name": "Simple Event Card",
            "html": """<div class="event-card">
                <h3>AI/ML Workshop for Beginners</h3>
                <p>Join us for a hands-on introduction to machine learning using Python and scikit-learn.</p>
                <span class="date">November 15, 2025 @ 6:00 PM EST</span>
                <span class="location">Tech Hub, 123 Broadway, NYC</span>
            </div>""",
            "type": "extraction"
        },
        {
            "id": "1.2",
            "name": "Multiple Events",
            "html": """<section>
                <div><h2>Blockchain Summit 2025</h2><time>Dec 1, 2025 9AM</time><p>350 5th Ave</p></div>
                <div><h2>React Native Workshop</h2><time>Dec 3, 2025 2PM</time><p>Online Event</p></div>
                <div><h2>Startup Pitch Night</h2><time>Dec 5, 2025 7PM</time><p>WeWork SoHo</p></div>
            </section>""",
            "type": "extraction"
        },
    ],
    "Set 2: Classification": [
        {
            "id": "2.1",
            "name": "AI/ML Event",
            "title": "Deep Learning for Computer Vision Workshop",
            "description": "Learn to build CNN models using TensorFlow and Keras. Hands-on training with image classification tasks.",
            "type": "classification"
        },
        {
            "id": "2.2",
            "name": "Ambiguous Event",
            "title": "Tech Meetup & Happy Hour",
            "description": "Casual networking event for tech professionals. Drinks, food, and conversations.",
            "type": "classification"
        },
    ],
    "Set 3: Tech Relevance": [
        {
            "id": "3.1",
            "name": "Obviously Tech",
            "title": "Introduction to Python Programming",
            "description": "Learn Python basics, variables, loops, functions, and build your first app.",
            "type": "tech_relevance"
        },
        {
            "id": "3.2",
            "name": "Tech-Adjacent",
            "title": "Digital Marketing Analytics Dashboard",
            "description": "Learn to track campaign performance using Google Analytics, Facebook Pixel, and custom dashboards.",
            "type": "tech_relevance"
        },
    ],
    "Set 4: Data Enrichment": [
        {
            "id": "4.2",
            "name": "Extract Tags",
            "title": "Building Scalable Microservices with Kubernetes and Docker",
            "description": "Learn container orchestration, service mesh architecture, and CI/CD pipelines for cloud-native applications.",
            "type": "tags"
        },
    ]
}


def run_test(manager: LLMManager, query_type: str, query_data: dict):
    """Run a single test query"""
    
    results = {}
    
    if query_type == "extraction":
        # Test event extraction
        html = query_data.get("html", "")
        
        start = time.time()
        try:
            events = manager.extract_events_from_html(html, "test")
            elapsed = time.time() - start
            
            results = {
                "success": True,
                "time": round(elapsed, 2),
                "events_found": len(events),
                "sample": events[0] if events else None
            }
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "time": round(time.time() - start, 2)
            }
    
    elif query_type == "classification":
        # Test event classification
        title = query_data.get("title", "")
        description = query_data.get("description", "")
        
        start = time.time()
        try:
            category = manager.classify_event_category(title, description)
            elapsed = time.time() - start
            
            results = {
                "success": True,
                "time": round(elapsed, 2),
                "category": category
            }
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "time": round(time.time() - start, 2)
            }
    
    elif query_type == "tech_relevance":
        # Test tech relevance detection
        title = query_data.get("title", "")
        description = query_data.get("description", "")
        
        start = time.time()
        try:
            result = manager.check_tech_relevance(title, description)
            elapsed = time.time() - start
            
            results = {
                "success": True,
                "time": round(elapsed, 2),
                "is_tech": result.get("is_tech_related", False),
                "confidence": result.get("confidence", 0.0),
                "reason": result.get("reason", "")
            }
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "time": round(time.time() - start, 2)
            }
    
    elif query_type == "tags":
        # Test tag extraction
        title = query_data.get("title", "")
        description = query_data.get("description", "")
        
        start = time.time()
        try:
            tags = manager.extract_tags(title, description)
            elapsed = time.time() - start
            
            results = {
                "success": True,
                "time": round(elapsed, 2),
                "tags": tags,
                "tag_count": len(tags)
            }
        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "time": round(time.time() - start, 2)
            }
    
    return results


def main():
    """Run all tests and generate comparison report"""
    
    print("🧪 LLM API Comparison Test Suite\n")
    print("=" * 80)
    
    # Initialize LLM Manager
    manager = LLMManager()
    
    available = manager.get_available_providers()
    print(f"\n✅ Available LLM Providers: {', '.join(available)}\n")
    
    if not available:
        print("❌ No LLM providers available. Please add API keys to .env")
        return
    
    # Run all tests
    all_results = {}
    
    for set_name, queries in QUERIES.items():
        print(f"\n📋 {set_name}")
        print("-" * 80)
        
        for query in queries:
            query_id = query["id"]
            query_name = query["name"]
            query_type = query["type"]
            
            print(f"\n   Query {query_id}: {query_name}")
            
            # Run test
            result = run_test(manager, query_type, query)
            
            # Store result
            all_results[query_id] = {
                "name": query_name,
                "type": query_type,
                "result": result
            }
            
            # Display result
            if result.get("success"):
                print(f"      ✅ Success ({result['time']}s)")
                
                if query_type == "extraction":
                    print(f"      📊 Found {result.get('events_found', 0)} events")
                elif query_type == "classification":
                    print(f"      🏷️  Category: {result.get('category', 'N/A')}")
                elif query_type == "tech_relevance":
                    print(f"      🔍 Tech: {result.get('is_tech', False)} (confidence: {result.get('confidence', 0):.2f})")
                elif query_type == "tags":
                    print(f"      🏷️  Tags: {', '.join(result.get('tags', [])[:5])}")
            else:
                print(f"      ❌ Failed: {result.get('error', 'Unknown error')}")
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("\n📊 SUMMARY REPORT\n")
    
    total_tests = len(all_results)
    successful = sum(1 for r in all_results.values() if r['result'].get('success'))
    total_time = sum(r['result'].get('time', 0) for r in all_results.values())
    
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {successful}/{total_tests} ({successful/total_tests*100:.0f}%)")
    print(f"   Total Time: {total_time:.2f}s")
    print(f"   Avg Time: {total_time/total_tests:.2f}s per query")
    
    # Save results to JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"llm_test_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'providers': available,
            'results': all_results,
            'summary': {
                'total_tests': total_tests,
                'successful': successful,
                'success_rate': successful/total_tests,
                'total_time': total_time,
                'avg_time': total_time/total_tests
            }
        }, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_file}")
    print("\n🎉 Testing complete!")
    print("\n💡 Next steps:")
    print("   1. Add more LLM API keys to .env for comparison")
    print("   2. Review TEST_QUERIES.md for all 20 test queries")
    print("   3. Compare results across different LLM providers")


if __name__ == "__main__":
    main()

