"""
Ollama Search API Accuracy & Performance Testing Script

This script tests Ollama's web_search and web_fetch capabilities for event extraction.
Measures accuracy, response time, and data completeness across various test scenarios.
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple
from ollama import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OLLAMA_API_KEY")
if not API_KEY:
    raise ValueError("OLLAMA_API_KEY not found in .env file")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {API_KEY}"}
)


class OllamaSearchTester:
    """Test Ollama Search API for accuracy and performance"""
    
    def __init__(self, model: str = "gpt-oss:20b"):
        self.model = model
        self.results = []
        
    def test_web_search(self, query: str, expected_count: int = None) -> Dict[str, Any]:
        """
        Test Ollama web_search with timing and result analysis.
        
        Args:
            query: Search query string
            expected_count: Expected number of results (optional)
            
        Returns:
            Dictionary with timing, result count, and quality metrics
        """
        print(f"\n🔍 Testing Web Search...")
        print(f"   Query: {query}")
        
        start_time = time.time()
        
        try:
            response = client.web_search(query)
            raw_results = response.get("results", [])
            
            # Convert to dicts
            results = []
            for r in raw_results:
                if hasattr(r, '__dict__'):
                    results.append({
                        'title': getattr(r, 'title', 'No Title'),
                        'url': getattr(r, 'url', '#'),
                        'content': getattr(r, 'content', 'No description')
                    })
                elif isinstance(r, dict):
                    results.append(r)
            
            elapsed = time.time() - start_time
            
            # Analyze results
            valid_urls = sum(1 for r in results if r.get('url') and r['url'] != '#')
            has_content = sum(1 for r in results if r.get('content') and len(r['content']) > 50)
            
            metrics = {
                'query': query,
                'elapsed_time': round(elapsed, 3),
                'result_count': len(results),
                'expected_count': expected_count,
                'valid_urls': valid_urls,
                'results_with_content': has_content,
                'success': True,
                'results': results[:5]  # Store first 5 for inspection
            }
            
            print(f"   ✅ Found {len(results)} results in {elapsed:.2f}s")
            print(f"   📊 Valid URLs: {valid_urls}/{len(results)}")
            print(f"   📄 With content: {has_content}/{len(results)}")
            
            return metrics
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Search failed: {str(e)}")
            
            return {
                'query': query,
                'elapsed_time': round(elapsed, 3),
                'success': False,
                'error': str(e)
            }
    
    def test_web_fetch(self, url: str, expected_fields: List[str] = None) -> Dict[str, Any]:
        """
        Test Ollama web_fetch with content analysis.
        
        Args:
            url: URL to fetch
            expected_fields: List of expected data fields (e.g., ['date', 'time', 'location'])
            
        Returns:
            Dictionary with fetch timing and content analysis
        """
        print(f"\n📄 Testing Web Fetch...")
        print(f"   URL: {url[:80]}...")
        
        start_time = time.time()
        
        try:
            response = client.web_fetch(url)
            elapsed = time.time() - start_time
            
            content = response.content if hasattr(response, 'content') else ""
            title = response.title if hasattr(response, 'title') else ""
            
            # Analyze content
            content_length = len(content)
            has_title = bool(title)
            
            # Check for expected data patterns
            found_patterns = {}
            if expected_fields:
                patterns = {
                    'date': ['january', 'february', 'march', 'april', 'may', 'june', 'july', 
                            'august', 'september', 'october', 'november', 'december', 
                            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
                            '2025', '2026'],
                    'time': ['am', 'pm', ':00', ':30', ':15', ':45'],
                    'location': ['street', 'avenue', 'ave', 'road', 'rd', 'blvd', 'ny', 'nyc', 'new york'],
                    'price': ['$', 'free', 'ticket', 'cost', 'price', 'usd'],
                    'registration': ['register', 'sign up', 'rsvp', 'ticket', 'purchase']
                }
                
                content_lower = content.lower()
                for field in expected_fields:
                    if field in patterns:
                        found = any(p in content_lower for p in patterns[field])
                        found_patterns[field] = found
            
            metrics = {
                'url': url,
                'elapsed_time': round(elapsed, 3),
                'content_length': content_length,
                'has_title': has_title,
                'title': title[:100] if title else None,
                'found_patterns': found_patterns,
                'content_preview': content[:500],
                'success': True
            }
            
            print(f"   ✅ Fetched {content_length} chars in {elapsed:.2f}s")
            print(f"   📝 Title: {title[:60]}..." if title else "   ⚠️  No title found")
            if found_patterns:
                print(f"   🔍 Pattern matches: {found_patterns}")
            
            return metrics
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Fetch failed: {str(e)}")
            
            return {
                'url': url,
                'elapsed_time': round(elapsed, 3),
                'success': False,
                'error': str(e)
            }
    
    def test_llm_extraction(self, content: str, extraction_task: str, expected_data: Dict = None) -> Dict[str, Any]:
        """
        Test LLM's ability to extract structured data from content.
        
        Args:
            content: Text content to analyze
            extraction_task: Description of what to extract
            expected_data: Optional dict of expected extracted values for accuracy scoring
            
        Returns:
            Dictionary with extraction results and accuracy metrics
        """
        print(f"\n🤖 Testing LLM Extraction...")
        print(f"   Task: {extraction_task[:80]}...")
        
        prompt = f"""{extraction_task}

CONTENT TO ANALYZE:
{content}

Return a JSON object with the extracted data. If a field is not found, use "Not found" as the value."""

        start_time = time.time()
        
        try:
            response = client.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            elapsed = time.time() - start_time
            llm_output = response.get('message', {}).get('content', '')
            
            # Try to parse JSON from response
            extracted_data = None
            try:
                # Look for JSON in the response
                if '{' in llm_output and '}' in llm_output:
                    json_start = llm_output.find('{')
                    json_end = llm_output.rfind('}') + 1
                    json_str = llm_output[json_start:json_end]
                    extracted_data = json.loads(json_str)
            except:
                pass
            
            # Calculate accuracy if expected data provided
            accuracy_score = None
            matched_fields = []
            if expected_data and extracted_data:
                total_fields = len(expected_data)
                matches = 0
                for key, expected_value in expected_data.items():
                    extracted_value = extracted_data.get(key, '')
                    if extracted_value and extracted_value != "Not found":
                        if str(expected_value).lower() in str(extracted_value).lower():
                            matches += 1
                            matched_fields.append(key)
                
                accuracy_score = round((matches / total_fields) * 100, 1) if total_fields > 0 else 0
            
            metrics = {
                'task': extraction_task[:100],
                'elapsed_time': round(elapsed, 3),
                'model': self.model,
                'extracted_data': extracted_data,
                'raw_output': llm_output[:500],
                'accuracy_score': accuracy_score,
                'matched_fields': matched_fields,
                'success': extracted_data is not None
            }
            
            print(f"   ✅ Extraction completed in {elapsed:.2f}s")
            if accuracy_score is not None:
                print(f"   🎯 Accuracy: {accuracy_score}% ({len(matched_fields)}/{len(expected_data)} fields)")
            if extracted_data:
                print(f"   📊 Extracted: {json.dumps(extracted_data, indent=2)[:200]}...")
            
            return metrics
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"   ❌ Extraction failed: {str(e)}")
            
            return {
                'task': extraction_task[:100],
                'elapsed_time': round(elapsed, 3),
                'success': False,
                'error': str(e)
            }
    
    def run_full_pipeline_test(self, search_query: str, extraction_fields: List[str]) -> Dict[str, Any]:
        """
        Run a complete test: search → fetch → extract
        
        Args:
            search_query: Query to search for
            extraction_fields: Fields to extract from fetched content
            
        Returns:
            Combined metrics from all stages
        """
        print(f"\n{'='*80}")
        print(f"🧪 FULL PIPELINE TEST")
        print(f"{'='*80}")
        
        pipeline_start = time.time()
        
        # Stage 1: Search
        search_result = self.test_web_search(search_query, expected_count=5)
        
        if not search_result.get('success') or not search_result.get('results'):
            print("   ❌ Pipeline failed at search stage")
            return {
                'search': search_result,
                'total_time': time.time() - pipeline_start,
                'success': False
            }
        
        # Stage 2: Fetch first result
        first_url = search_result['results'][0].get('url')
        if not first_url or first_url == '#':
            print("   ❌ No valid URL to fetch")
            return {
                'search': search_result,
                'total_time': time.time() - pipeline_start,
                'success': False
            }
        
        fetch_result = self.test_web_fetch(first_url, expected_fields=extraction_fields)
        
        if not fetch_result.get('success'):
            print("   ❌ Pipeline failed at fetch stage")
            return {
                'search': search_result,
                'fetch': fetch_result,
                'total_time': time.time() - pipeline_start,
                'success': False
            }
        
        # Stage 3: Extract with LLM
        content = fetch_result.get('content_preview', '')
        extraction_task = f"Extract the following fields from this event page content: {', '.join(extraction_fields)}. Return as JSON."
        
        extract_result = self.test_llm_extraction(content, extraction_task)
        
        total_time = time.time() - pipeline_start
        
        print(f"\n{'='*80}")
        print(f"✅ Pipeline completed in {total_time:.2f}s")
        print(f"{'='*80}")
        
        return {
            'search': search_result,
            'fetch': fetch_result,
            'extract': extract_result,
            'total_time': round(total_time, 3),
            'success': True
        }
    
    def save_results(self, filename: str = None):
        """Save all test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ollama_test_results_{timestamp}.json"
        
        output_path = os.path.join(os.getcwd(), filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'model': self.model,
                'results': self.results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
        return output_path


def run_test_suite():
    """Run comprehensive test suite based on TEST_QUERIES.md scenarios"""
    
    tester = OllamaSearchTester(model="gpt-oss:20b")
    
    print("="*80)
    print("🧪 OLLAMA SEARCH API TESTING SUITE")
    print("="*80)
    print(f"Model: {tester.model}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Test 1: Basic Event Search (Eventbrite)
    print("\n\n📋 TEST 1: EVENTBRITE EVENT SEARCH")
    print("-"*80)
    result1 = tester.run_full_pipeline_test(
        search_query="site:eventbrite.com/e/ NYC tech AI startup networking October 2025",
        extraction_fields=['date', 'time', 'location', 'price']
    )
    tester.results.append({'test_name': 'Eventbrite Event Search', **result1})
    
    # Test 2: Luma Event Search
    print("\n\n📋 TEST 2: LUMA EVENT SEARCH")
    print("-"*80)
    result2 = tester.run_full_pipeline_test(
        search_query="site:lu.ma NYC AI meetup October 2025",
        extraction_fields=['date', 'time', 'location', 'price']
    )
    tester.results.append({'test_name': 'Luma Event Search', **result2})
    
    # Test 3: Direct URL Fetch Test (known Eventbrite event)
    print("\n\n📋 TEST 3: DIRECT URL FETCH TEST")
    print("-"*80)
    print("Testing fetch accuracy on a known event URL...")
    
    # Use a URL from previous search if available
    test_url = None
    if result1.get('success') and result1['search'].get('results'):
        test_url = result1['search']['results'][0]['url']
    
    if test_url:
        fetch_detail = tester.test_web_fetch(
            url=test_url,
            expected_fields=['date', 'time', 'location', 'price', 'registration']
        )
        tester.results.append({'test_name': 'Direct URL Fetch', **fetch_detail})
    else:
        print("   ⚠️  Skipped - no valid URL from previous tests")
    
    # Test 4: LLM Extraction Accuracy (with known content)
    print("\n\n📋 TEST 4: LLM EXTRACTION ACCURACY")
    print("-"*80)
    
    sample_content = """
    AI & Tech Networking NYC Manhattan
    
    Join us for an exciting evening of networking with NYC's top tech professionals!
    
    Event Details:
    📅 Date: October 22, 2025
    ⏰ Time: 6:00 PM - 9:00 PM
    📍 Location: The Tech Hub, 77 East 7th Street, New York, NY 10003
    💰 Price: $44.51 (Early bird: $35.00)
    
    Event Schedule:
    • 6:00 PM - Registration & Welcome Drinks
    • 7:40 PM - Startup Pitches
    • 9:00 PM - Event Ends
    
    This event is perfect for startup founders, developers, investors, and tech enthusiasts!
    """
    
    extraction_result = tester.test_llm_extraction(
        content=sample_content,
        extraction_task="Extract event date, time, location (full address), and price information",
        expected_data={
            'date': 'October 22, 2025',
            'time': '6:00 PM - 9:00 PM',
            'location': '77 East 7th Street, New York, NY 10003',
            'price': '$44.51'
        }
    )
    tester.results.append({'test_name': 'LLM Extraction Accuracy', **extraction_result})
    
    # Test 5: Search Result Quality (multiple queries)
    print("\n\n📋 TEST 5: SEARCH RESULT QUALITY COMPARISON")
    print("-"*80)
    
    queries = [
        "NYC tech events October 2025",
        "site:eventbrite.com NYC AI conference",
        "site:lu.ma Brooklyn startup meetup"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n   Query {i}/{len(queries)}")
        search_result = tester.test_web_search(query, expected_count=5)
        tester.results.append({'test_name': f'Search Quality Test {i}', **search_result})
        time.sleep(1)  # Rate limiting
    
    # Generate Summary
    print("\n\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    successful_tests = sum(1 for r in tester.results if r.get('success', False))
    total_tests = len(tester.results)
    avg_search_time = sum(r.get('elapsed_time', 0) for r in tester.results if 'search' in r.get('test_name', '').lower()) / max(1, sum(1 for r in tester.results if 'search' in r.get('test_name', '').lower()))
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Successful: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")
    print(f"Average Search Time: {avg_search_time:.2f}s")
    
    # Save results
    tester.save_results()
    
    return tester.results


if __name__ == "__main__":
    try:
        results = run_test_suite()
        print("\n✅ Testing complete!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
