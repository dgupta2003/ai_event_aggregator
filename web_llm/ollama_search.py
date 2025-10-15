import os
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from ollama import Client
from typing import List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get Ollama API key from environment
API_KEY = os.getenv("OLLAMA_API_KEY")

if not API_KEY:
    raise ValueError("OLLAMA_API_KEY not found in .env file")

client = Client(
    host="https://ollama.com",  # Use the cloud endpoint
    headers={"Authorization": f"Bearer {API_KEY}"}
)

@tool
def ollama_web_search(query: str) -> List[Dict[str, Any]]:
    """
    Search the web using Ollama's web search API.

    Args:
        query: The search query string and get the top 10 results ONLY and no more.

    Returns:
        List of search results with title, url, and content.
    """
    try:
        response = client.web_search(query)
        raw_results = response.get("results", [])
        
        # Convert objects to dicts to avoid serialization issues
        results = []
        for r in raw_results[:10]:
            if hasattr(r, '__dict__'):
                # Convert object to dict
                results.append({
                    'title': getattr(r, 'title', 'No Title'),
                    'url': getattr(r, 'url', '#'),
                    'content': getattr(r, 'content', 'No description')
                })
            elif isinstance(r, dict):
                results.append(r)
        
        return results
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


@tool
def ollama_web_fetch(url: str) -> Dict[str, Any]:
    """
    Fetch content from a specific URL using Ollama's web fetch API.

    Args:
        url: The URL to fetch content from.

    Returns:
        Dictionary with title, content, and links from the page.
    """
    try:
        response = client.web_fetch(url)
        return {
            "title": response.title,
            "content": response.content,
            "links": response.links
        }
    except Exception as e:
        return {"error": f"Fetch failed: {str(e)}"}


def analyze_with_llm(search_results: List[Dict[str, Any]], query: str) -> str:
    """
    Use Ollama LLM to analyze and summarize search results.
    
    Args:
        search_results: List of search result dictionaries
        query: Original search query
        
    Returns:
        LLM-generated analysis and summary
    """
    try:
        # Format search results for LLM
        formatted_results = "\n\n".join([
            f"Event {i+1}:\nTitle: {r.get('title', 'N/A')}\nURL: {r.get('url', '#')}\nDescription: {r.get('content', 'No description')[:500]}"
            for i, r in enumerate(search_results[:10])
        ])
        
        # Create prompt for LLM
        prompt = f"""You are an expert event curator for NYC tech professionals. 

I searched for: "{query}"

Here are the search results I found:

{formatted_results}

Please analyze these events and provide:
1. A brief summary of the top 3-5 most relevant events
2. Key highlights (dates, types of events, who should attend)
3. Any notable patterns or recommendations

Keep your response concise and actionable."""

        # Use Ollama chat completion - try without specifying model (uses default)
        response = client.chat(
            model="gpt-oss:20b",  # Use gpt-oss with size specification
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.get('message', {}).get('content', 'No analysis available')
    
    except Exception as e:
        # Fallback to simple formatting if LLM fails
        error_msg = str(e)
        print(f"⚠️  LLM Error: {error_msg}")
        
        # Provide a basic summary instead
        summary = f"""**Search Summary**

Found {len(search_results)} events for: "{query}"

**Top Events:**
"""
        for i, r in enumerate(search_results[:5], 1):
            summary += f"\n{i}. **{r.get('title', 'No Title')}**\n   {r.get('url', '#')}\n"
        
        return summary


def fetch_event_details(url: str) -> Dict[str, Any]:
    """
    Fetch detailed content from an event page using Ollama's web fetch.
    
    Args:
        url: The event URL to fetch
        
    Returns:
        Dictionary with extracted event details
    """
    try:
        print(f"  🔍 Fetching details from: {url}")
        response = client.web_fetch(url)
        
        return {
            "url": url,
            "title": response.title if hasattr(response, 'title') else "N/A",
            "content": response.content if hasattr(response, 'content') else "N/A",
            "links": response.links if hasattr(response, 'links') else []
        }
    except Exception as e:
        print(f"  ❌ Failed to fetch {url}: {str(e)}")
        return {
            "url": url,
            "title": "N/A",
            "content": f"Failed to fetch: {str(e)}",
            "links": []
        }


def synthesize_with_llm(event_details: List[Dict[str, Any]], query: str) -> str:
    """
    Synthesize detailed event information with LLM into a comprehensive report.
    
    Args:
        event_details: List of detailed event data dictionaries
        query: Original search query
        
    Returns:
        LLM-generated comprehensive event report
    """
    try:
        # Format detailed event data for LLM with more content
        formatted_events = ""
        for i, event in enumerate(event_details, 1):
            content = event.get('content', 'No content')
            event_url = event.get('url', '#')
            # Provide more content to LLM (up to 3000 chars per event)
            formatted_events += f"""
EVENT {i}:
Title: {event.get('title', 'N/A')}
REGISTRATION URL (USE THIS EXACT URL): {event_url}

FULL CONTENT:
{content[:3000]}

{'='*80}
"""
        
        # Create comprehensive prompt for LLM synthesis with explicit extraction instructions
        prompt = f"""You are an expert at extracting structured event information. I searched for: "{query}"

I've fetched the FULL CONTENT from these event pages. Your job is to EXTRACT SPECIFIC DATA from the content provided.

{formatted_events}

**CRITICAL INSTRUCTIONS - READ CAREFULLY:**

1. For EACH event, you MUST carefully read the FULL CONTENT section
2. For the Registration URL field, use the EXACT "REGISTRATION URL" provided
3. Extract information by looking for these patterns in the content:

   **DATE EXTRACTION:**
   - Look for: "October X", "Oct X", specific dates like "October 7", "Oct 15 2025"
   - Look for: "📅", "Date:", "When:", calendar emoji
   - If it says "Every month" or "Monthly", write: "Monthly recurring event (check event page for next date)"
   
   **TIME EXTRACTION:**
   - Look for: "6:00 PM", "11:00 AM - 4:00 PM", "Event Start: 6:00 PM", "7:40 PM", etc.
   - Look for: "⏰", "Time:", schedule sections
   - Extract ALL times mentioned (start time, pitch time, end time)
   
   **LOCATION EXTRACTION:**
   - Look for: venue names like "Whiskey Cellar NYC", "Brooklyn", "Dumbo"
   - Look for: addresses with street numbers and names like "77 East 7th Street"
   - Look for: "📍", "Location:", "Where:", "Venue:"
   - Extract the FULL address if present
   
   **PRICE EXTRACTION:**
   - Look for: "$" followed by numbers like "$44.51", "$0", "$10-$50"
   - Look for: "Free", "free admission", "Purchase ticket", "Early bird"
   - Look for: "💰", "Price:", "Cost:", "Ticket:"
   - If it mentions "Purchase ticket" but no price, write: "Paid (price on event page)"

4. IMPORTANT: If you find ANY of this information in the content, EXTRACT IT and include it. DO NOT say "Check event page for details" if the info is in the content I provided.

5. Only write "Check event page for details" if the information is genuinely NOT in the content after thoroughly reading it.

Create a professional markdown report with:

## Featured Events

For each event, use this EXACT format:

### [Number]. [Event Name] [emoji]

**📅 Date & Time:** [Extract EXACT date and time from content - include start time, end time if available. If monthly recurring, say so]  
**📍 Location:** [Extract EXACT venue name and address from content]  
**💰 Price:** [Extract EXACT price from content like "$44.51", "Free", or "Paid (price on event page)" if it says purchase but no amount]  
**🔗 Registration:** [Use the EXACT "REGISTRATION URL" provided - do not modify]

**About:** [1-2 sentences about the event]

**Who Should Attend:** [Target audience from content]

---

EXAMPLE of what I expect:
If content says "Event Start: 6:00 PM • Event End: 9:00 PM" 
→ You write: "6:00 PM - 9:00 PM"

If content says "77 East 7th Street New York, NY 10003"
→ You write: "77 East 7th Street, New York, NY 10003"

Now create the report:"""

        response = client.chat(
            model="gpt-oss:20b",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.get('message', {}).get('content', 'No synthesis available')
    
    except Exception as e:
        print(f"⚠️  LLM Synthesis Error: {str(e)}")
        
        # Fallback formatting
        fallback = f"""# Event Discovery Report

**Query:** {query}

## Events Found

"""
        for i, event in enumerate(event_details, 1):
            fallback += f"""### {i}. {event.get('title', 'No Title')}

**URL:** {event.get('url', '#')}

**Description:** {event.get('content', 'No description')[:500]}...

---

"""
        return fallback


# Create the LLM - Configure to use cloud Ollama endpoint
llm = ChatOllama(
    model="gpt-oss:20b",  # Use gpt-oss:20b (exists on cloud)
    temperature=0.7,
    base_url="https://ollama.com",
    api_key=API_KEY
)

# Define tools
tools = [ollama_web_search, ollama_web_fetch]

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant that can search the web and fetch web pages.
When users ask questions, use the web search tool to find current information.
If you need to get detailed information from a specific URL, use the web fetch tool.
Always provide accurate and up-to-date information based on your search results."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create the agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def save_results_to_markdown(results: Dict[str, Any], filename: str = None) -> str:
    """
    Save search results to a markdown file.
    
    Args:
        results: Dictionary containing the search results
        filename: Optional custom filename. If not provided, generates timestamp-based name
        
    Returns:
        Path to the saved markdown file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nyc_tech_events_{timestamp}.md"
    
    # Ensure .md extension
    if not filename.endswith('.md'):
        filename += '.md'
    
    markdown_content = f"""# NYC Tech Events Discovery Report

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}  
**Search Query:** {results.get('query', 'N/A')}  
**Sources:** Eventbrite & Luma  
**Total Events Found:** {results.get('result_count', 'Unknown')}

---

{results.get('output', 'No results found')}

---

## Sources & Attribution

- **Eventbrite:** https://www.eventbrite.com
- **Luma:** https://lu.ma
- **AI Model:** gpt-oss:20b (Ollama Cloud)
- **Search Engine:** Ollama Web Search

---

*This report was automatically generated by an AI-powered event discovery system. Event details are extracted from public sources and synthesized using advanced language models. Please verify all information directly with event organizers.*
"""
    
    # Save to file
    output_path = os.path.join(os.getcwd(), filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return output_path


def format_search_results(raw_results: List[Dict[str, Any]]) -> str:
    """
    Format raw search results into readable markdown.
    
    Args:
        raw_results: List of search result dictionaries
        
    Returns:
        Formatted markdown string
    """
    if not raw_results or (len(raw_results) == 1 and 'error' in raw_results[0]):
        return "No results found or search failed."
    
    markdown = ""
    for i, result in enumerate(raw_results[:10], 1):  # Limit to top 10
        if 'error' in result:
            continue
            
        title = result.get('title', 'No Title')
        url = result.get('url', '#')
        content = result.get('content', 'No description available')
        
        # Truncate content if too long
        if len(content) > 300:
            content = content[:297] + "..."
        
        markdown += f"""
### {i}. {title}

**URL:** [{url}]({url})

**Description:**  
{content}

---
"""
    
    return markdown if markdown else "No valid results found."


# Example usage
if __name__ == "__main__":
    print("🔍 EVENT DISCOVERY SYSTEM (Perplexity-style)")
    print("=" * 80)
    print("Finding and analyzing NYC tech events from Eventbrite & Luma...")
    print("=" * 80)
    
    # Search queries for both platforms - more specific to get individual events
    queries = [
        "site:eventbrite.com/e/ NYC tech AI startup networking October 2025",
        "site:lu.ma NYC tech AI networking October 2025 -calendar -events/nyc"
    ]
    
    all_search_results = []
    
    # Step 1: Search both platforms
    print("\n📊 STEP 1: SEARCHING EVENT PLATFORMS")
    print("-" * 80)
    
    for query in queries:
        platform = "Eventbrite" if "eventbrite" in query else "Luma"
        print(f"\n� Searching {platform}...")
        
        search_results = ollama_web_search.invoke(query)
        
        if search_results and not (len(search_results) == 1 and 'error' in search_results[0]):
            print(f"   ✅ Found {len(search_results)} results from {platform}")
            all_search_results.extend(search_results)
        else:
            print(f"   ⚠️  No results from {platform}")
    
    if not all_search_results:
        print("\n❌ No events found. Exiting...")
        exit(1)
    
    print(f"\n✅ Total search results: {len(all_search_results)}")
    
    # Step 2: Fetch detailed content from event URLs
    print("\n📄 STEP 2: FETCHING DETAILED EVENT INFORMATION")
    print("-" * 80)
    
    event_details = []
    # Limit to top 10 events to avoid rate limiting
    for result in all_search_results[:10]:
        url = result.get('url', '')
        if url and url != '#':
            details = fetch_event_details(url)
            if details.get('content') != 'N/A':
                event_details.append(details)
                # Debug: Show first 500 chars of content
                content_preview = details.get('content', '')[:500]
                print(f"     📝 Content preview: {content_preview}...\n")
    
    print(f"\n✅ Successfully fetched details for {len(event_details)} events")
    
    # Step 3: Synthesize with LLM
    print("\n🤖 STEP 3: AI SYNTHESIS & ANALYSIS")
    print("-" * 80)
    
    combined_query = "NYC tech events in October 2025 from Eventbrite and Luma including AI, startup, networking, and tech meetups"
    
    print("   Generating comprehensive event report with AI...")
    synthesis = synthesize_with_llm(event_details, combined_query)
    
    # Step 4: Display results
    print("\n" + "=" * 80)
    print("📋 EVENT DISCOVERY REPORT")
    print("=" * 80)
    print(synthesis)
    print("\n" + "=" * 80)
    
    # Step 5: Save to markdown
    print("\n💾 STEP 4: SAVING REPORT")
    print("-" * 80)
    
    result_data = {
        "query": combined_query,
        "output": synthesis,
        "result_count": len(event_details)
    }
    
    saved_file = save_results_to_markdown(result_data)
    
    print(f"   ✅ Report saved to: {saved_file}")
    print("\n" + "=" * 80)
    print("🎉 EVENT DISCOVERY COMPLETE!")
    print("=" * 80)
