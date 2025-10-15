# 🧪 LLM API Test Queries for Event Scraping

## Purpose
Compare 4 different LLM APIs (GPT-4, Claude, Gemini, Groq) across different event-related tasks to determine which performs best for each use case.

---

## 📋 **Set 1: Event Extraction from HTML**
*Test: How well can the LLM extract structured event data from messy HTML?*

### Query 1.1: Simple Event Card
```
Extract event details from this HTML:

<div class="event-card">
    <h3>AI/ML Workshop for Beginners</h3>
    <p>Join us for a hands-on introduction to machine learning using Python and scikit-learn.</p>
    <span class="date">November 15, 2025 @ 6:00 PM EST</span>
    <span class="location">Tech Hub, 123 Broadway, NYC</span>
</div>

Return JSON with: title, description, start_time (ISO format), venue_name, city
```

### Query 1.2: Multiple Events
```
Extract ALL events from this HTML:

<section>
    <div><h2>Blockchain Summit 2025</h2><time>Dec 1, 2025 9AM</time><p>350 5th Ave</p></div>
    <div><h2>React Native Workshop</h2><time>Dec 3, 2025 2PM</time><p>Online Event</p></div>
    <div><h2>Startup Pitch Night</h2><time>Dec 5, 2025 7PM</time><p>WeWork SoHo</p></div>
</section>

Return a JSON array of events with: title, start_time, venue_name, is_online
```

### Query 1.3: Messy/Inconsistent HTML
```
Extract event data from this poorly formatted HTML:

<div>
    <b>EVENT:</b> Cybersecurity Bootcamp<br>
    When: 2025-11-20 at 10AM-5PM<br>
    WHERE: Cyber Defense Center, Austin TX<br>
    COST: $299 (Early bird: $199)<br>
    Learn ethical hacking & penetration testing!<br>
</div>

Return JSON with: title, description, start_time, end_time, venue_name, city, state, price
```

### Query 1.4: Event with Rich Metadata
```
Extract comprehensive event details:

<article class="lu-event">
    <h1>Web3 Developer Conference 2025</h1>
    <div class="meta">
        <span>📅 Jan 10-12, 2025</span>
        <span>📍 Moscone Center, San Francisco</span>
        <span>💰 $599-$999</span>
        <span>👥 2000+ attendees expected</span>
    </div>
    <p>3-day conference featuring talks from Ethereum founders, Web3 workshops, and networking.</p>
    <ul class="topics">
        <li>Smart Contracts</li>
        <li>DeFi</li>
        <li>NFTs</li>
    </ul>
</article>

Return JSON with: title, description, start_time, end_time, venue_name, city, price, capacity, tags
```

### Query 1.5: Hidden/Dynamic Content
```
This HTML has data in non-obvious places:

<div data-event-id="evt123" data-title="DevOps Meetup" data-date="2025-11-18T19:00:00Z">
    <img src="event.jpg" alt="DevOps Meetup - Nov 18, 7PM at Google NYC">
    <meta itemprop="location" content="Google NYC, 111 8th Ave">
    <script type="application/ld+json">
    {
        "startDate": "2025-11-18T19:00:00",
        "endDate": "2025-11-18T21:00:00",
        "name": "DevOps Meetup",
        "location": "Google NYC"
    }
    </script>
</div>

Extract: title, start_time, end_time, venue_name from ANY part of this HTML (attributes, alt text, JSON-LD)
```

---

## 🎯 **Set 2: Event Classification & Categorization**
*Test: How accurately can the LLM categorize events into specific types?*

### Query 2.1: AI/ML Event
```
Classify this event into ONE category:

Title: "Deep Learning for Computer Vision Workshop"
Description: "Learn to build CNN models using TensorFlow and Keras. Hands-on training with image classification tasks."

Categories: ai_ml, data_science, web_dev, mobile, devops, blockchain, security, startup, networking, workshop, conference, other

Return: {"category": "...", "confidence": 0.0-1.0, "reason": "brief explanation"}
```

### Query 2.2: Ambiguous Event
```
Classify this event:

Title: "Tech Meetup & Happy Hour"
Description: "Casual networking event for tech professionals. Drinks, food, and conversations."

Categories: ai_ml, data_science, web_dev, mobile, devops, blockchain, security, startup, networking, workshop, conference, other

Return: {"category": "...", "confidence": 0.0-1.0, "reason": "..."}
```

### Query 2.3: Multi-Topic Event
```
Classify this event (pick the MOST relevant category):

Title: "Full Stack Developer Bootcamp: React + Node.js + MongoDB + AWS Deployment"
Description: "12-week intensive bootcamp covering frontend, backend, databases, and cloud deployment."

Categories: web_dev, mobile, devops, workshop, conference

Return: {"category": "...", "confidence": 0.0-1.0, "reason": "..."}
```

### Query 2.4: Non-Tech Event
```
Is this a tech event? Classify it:

Title: "Yoga & Meditation for Startup Founders"
Description: "De-stress and find balance. Weekly yoga sessions designed for busy entrepreneurs."

Categories: startup, networking, wellness, other

Return: {"category": "...", "is_tech_related": true/false, "confidence": 0.0-1.0}
```

### Query 2.5: Blockchain/Web3 Event
```
Classify this event:

Title: "NFT Art Exhibition & Smart Contract Workshop"
Description: "Explore digital art on the blockchain. Learn to mint NFTs and write Solidity contracts."

Categories: blockchain, ai_ml, workshop, conference, other

Return: {"category": "...", "subcategories": ["..."], "confidence": 0.0-1.0}
```

---

## 🔍 **Set 3: Tech Relevance Detection**
*Test: Can the LLM accurately determine if an event is tech-related?*

### Query 3.1: Obviously Tech
```
Is this event tech-related?

Title: "Introduction to Python Programming"
Description: "Learn Python basics, variables, loops, functions, and build your first app."

Return: {"is_tech_related": true/false, "confidence": 0.0-1.0, "tech_keywords": ["..."], "reason": "..."}
```

### Query 3.2: Tech-Adjacent
```
Is this event tech-related?

Title: "Digital Marketing Analytics Dashboard"
Description: "Learn to track campaign performance using Google Analytics, Facebook Pixel, and custom dashboards."

Return: {"is_tech_related": true/false, "confidence": 0.0-1.0, "tech_keywords": ["..."], "reason": "..."}
```

### Query 3.3: Not Tech
```
Is this event tech-related?

Title: "Real Estate Investment Strategies"
Description: "Learn how to identify undervalued properties and maximize rental income."

Return: {"is_tech_related": true/false, "confidence": 0.0-1.0, "tech_keywords": ["..."], "reason": "..."}
```

### Query 3.4: Hardware/IoT
```
Is this event tech-related?

Title: "Arduino & Raspberry Pi Maker Workshop"
Description: "Build smart home devices using microcontrollers. Beginner-friendly electronics projects."

Return: {"is_tech_related": true/false, "confidence": 0.0-1.0, "tech_keywords": ["..."], "reason": "..."}
```

### Query 3.5: Borderline Case
```
Is this event tech-related?

Title: "Biotech Startup Pitch Competition"
Description: "Watch biotech and healthtech startups pitch to investors. Focus on medical devices and pharmaceutical innovations."

Return: {"is_tech_related": true/false, "confidence": 0.0-1.0, "tech_keywords": ["..."], "reason": "..."}
```

---

## ✨ **Set 4: Data Enrichment & Enhancement**
*Test: Can the LLM improve incomplete or poor-quality event data?*

### Query 4.1: Expand Short Description
```
Enhance this event description (keep it 2-3 sentences, informative):

Title: "Hack Night"
Description: "Come code"

Enhanced description should explain what attendees will do, what they'll learn, and who should attend.
```

### Query 4.2: Extract Tags from Text
```
Extract 5-10 relevant tags from this event:

Title: "Building Scalable Microservices with Kubernetes and Docker"
Description: "Learn container orchestration, service mesh architecture, and CI/CD pipelines for cloud-native applications."

Return: {"tags": ["tag1", "tag2", ...], "primary_topic": "...", "skill_level": "beginner/intermediate/advanced"}
```

### Query 4.3: Infer Missing Information
```
This event is missing details. Infer likely values:

Title: "Women in Tech Leadership Summit"
Description: "Annual conference celebrating women leaders in technology."
Venue: "Convention Center"
City: [MISSING]
State: [MISSING]

Based on "Convention Center" being a common venue, what city/state is this MOST likely in? Return top 3 possibilities with confidence.
```

### Query 4.4: Standardize Date Format
```
Convert these dates to ISO 8601 format (YYYY-MM-DDTHH:MM:SS):

1. "Nov 15th, 2025 at 6pm EST"
2. "12/01/2025 9:00 AM PST"
3. "2025-10-20 18:00"
4. "Tomorrow at 7PM" (assume today is 2025-10-13)
5. "Next Monday 10AM" (assume today is 2025-10-13)

Return JSON array of {original: "...", iso: "...", timezone: "..."}
```

### Query 4.5: Detect and Fix Errors
```
This event data has errors. Identify and fix them:

{
  "title": "AI WORSHOP!!!",
  "description": "lern about AI and machne lerning",
  "start_time": "2025-13-45T25:00:00",
  "end_time": "2025-10-15T14:00:00",
  "venue_name": "tech hub nyc",
  "city": "new york",
  "price": "$free"
}

Return corrected JSON with: {
  "errors_found": ["..."],
  "corrections": {"field": "old → new"},
  "fixed_data": {...}
}
```

---

## 📊 **Evaluation Criteria**

For each query, score the LLM response on:

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Accuracy** | 40% | Correctly extracted/classified data |
| **Completeness** | 25% | Found all available information |
| **Format** | 15% | Returned valid JSON as requested |
| **Speed** | 10% | Response time (seconds) |
| **Cost** | 10% | API cost per query |

---

## 🎯 **Expected LLM Performance**

| LLM | Best For | Weakest At | Cost |
|-----|----------|------------|------|
| **GPT-4** | Complex extraction (1.1-1.5) | Speed | $$$$ |
| **Claude** | Classification (2.1-2.5) | Structured output | $$$ |
| **Gemini** | Text enhancement (4.1-4.2) | Complex reasoning | $ |
| **Groq (Llama)** | Simple binary checks (3.1-3.5) | Nuanced understanding | FREE |

---

## 🧪 **How to Run Tests**

```python
# test_llm_comparison.py
from src.processing.llm_manager import LLMManager
import time
import json

manager = LLMManager()

# Test Query 1.1 on all available LLMs
query = "Extract event details from this HTML: ..."

results = {}
for provider in manager.get_available_providers():
    start = time.time()
    
    # Run query on each LLM
    response = manager.extract_events_from_html(query, provider)
    
    results[provider] = {
        'response': response,
        'time': time.time() - start,
        'cost': estimate_cost(provider, query)
    }

print(json.dumps(results, indent=2))
```

---

## 📈 **Results Template**

| Query | GPT-4 | Claude | Gemini | Groq | Winner |
|-------|-------|--------|--------|------|--------|
| 1.1 Simple Extraction | 95% | 90% | 85% | 75% | GPT-4 |
| 1.2 Multiple Events | 98% | 92% | 88% | 70% | GPT-4 |
| 2.1 AI/ML Classification | 95% | **98%** | 90% | 85% | Claude |
| 3.1 Tech Detection | 92% | 94% | 88% | **95%** | Groq |
| 4.1 Description Enhancement | 90% | 88% | **95%** | 80% | Gemini |

---

**Save these queries and use them to benchmark your multi-LLM system!** 🚀

