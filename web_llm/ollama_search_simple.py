import os
from ollama import Client
from typing import List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables from .env file
load_dotenv()

# Get Ollama API key from environment
API_KEY = os.getenv("OLLAMA_API_KEY")

if not API_KEY:
    raise ValueError("OLLAMA_API_KEY not found in .env file")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {API_KEY}"}
)


def search_nyc_tech_events(query: str) -> Dict[str, Any]:
    """
    Search for NYC tech events using Ollama web search.
    
    Args:
        query: Search query string
        
    Returns:
        Dictionary with search results
    """
    try:
        print(f"🔍 Searching: {query}")
        response = client.web_search(query)
        raw_results = response.get("results", [])
        
        # Convert results to dict format (handle WebSearchResult objects)
        results = []
        for r in raw_results[:10]:
            if hasattr(r, '__dict__'):
                # Convert object to dict
                results.append({
                    'title': getattr(r, 'title', 'N/A'),
                    'url': getattr(r, 'url', '#'),
                    'content': getattr(r, 'content', 'No description')
                })
            elif isinstance(r, dict):
                results.append(r)
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


def format_results_to_markdown(search_data: Dict[str, Any], filename: str = None) -> str:
    """
    Save search results to a markdown file.
    
    Args:
        search_data: Dictionary containing search results
        filename: Optional custom filename
        
    Returns:
        Path to saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nyc_tech_events_{timestamp}.md"
    
    if not filename.endswith('.md'):
        filename += '.md'
    
    # Build markdown content
    markdown = f"""# NYC Tech Events Search Results

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

---

## Query
{search_data.get('query', 'N/A')}

---

## Search Results

"""
    
    if not search_data.get('success'):
        markdown += f"""
### ❌ Search Failed

**Error:** {search_data.get('error', 'Unknown error')}

Please check:
- API key is valid
- Internet connection is working
- Ollama cloud service is accessible
"""
    else:
        results = search_data.get('results', [])
        
        if not results:
            markdown += "No results found.\n"
        else:
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No Title')
                url = result.get('url', '#')
                content = result.get('content', 'No description available')
                
                # Truncate long content
                if len(content) > 400:
                    content = content[:397] + "..."
                
                markdown += f"""
### {i}. {title}

**URL:** [{url}]({url})

**Description:**  
{content}

---

"""
    
    markdown += f"""
## Search Metadata

- **Total Results Found:** {search_data.get('total', 0)}
- **Search Type:** Ollama Web Search API
- **Timestamp:** {datetime.now().isoformat()}

---

*Generated automatically by NYC Tech Event Discovery System*
"""
    
    # Save file
    output_path = os.path.join(os.getcwd(), filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    return output_path


def display_results(search_data: Dict[str, Any]):
    """Pretty print search results to console."""
    print("\n" + "=" * 80)
    
    if not search_data.get('success'):
        print("❌ SEARCH FAILED")
        print(f"Error: {search_data.get('error')}")
        return
    
    print(f"✅ FOUND {search_data.get('total', 0)} RESULTS")
    print("=" * 80)
    
    results = search_data.get('results', [])
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'No Title')}")
        print(f"   URL: {result.get('url', '#')}")
        
        content = result.get('content', 'No description')
        if len(content) > 150:
            content = content[:147] + "..."
        print(f"   {content}")
        print()


def main():
    """Main execution function."""
    print("=" * 80)
    print(" " * 20 + "🗽 NYC TECH EVENT SEARCH 🗽")
    print("=" * 80)
    
    # Search query
    query = "top tech events in New York City October 2025 including AI, startup, networking, meetups"
    
    # Perform search
    search_results = search_nyc_tech_events(query)
    
    # Display results
    display_results(search_results)
    
    # Save to markdown
    if search_results.get('success'):
        saved_file = format_results_to_markdown(search_results)
        print("\n" + "=" * 80)
        print(f"💾 Results saved to: {saved_file}")
        print("=" * 80)
        
        # Also save raw JSON for debugging
        json_file = saved_file.replace('.md', '.json')
        with open(json_file, 'w') as f:
            json.dump(search_results, f, indent=2)
        print(f"📊 Raw data saved to: {json_file}")
        print("=" * 80)
    else:
        print("\n⚠️  Search failed - no file saved")


if __name__ == "__main__":
    main()
