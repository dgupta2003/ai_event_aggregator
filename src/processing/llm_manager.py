"""
Multi-LLM Manager

This module manages multiple LLM providers (OpenAI, Anthropic, Google, etc.)
and routes tasks to the most appropriate model for each job.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from enum import Enum
import os

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    LOCAL = "local"


class LLMTask(str, Enum):
    """Different tasks that can be performed"""
    EXTRACT_EVENTS = "extract_events"
    CLASSIFY_CATEGORY = "classify_category"
    ENHANCE_DESCRIPTION = "enhance_description"
    TECH_RELEVANCE = "tech_relevance"
    VALIDATE_DATA = "validate_data"
    EXTRACT_TAGS = "extract_tags"
    SUMMARIZE = "summarize"


class LLMManager:
    """Manages multiple LLM providers and routes tasks appropriately"""
    
    def __init__(self):
        self.logger = logging.getLogger("llm_manager")
        
        # Initialize available providers
        self.providers = {}
        self._initialize_providers()
        
        # Task routing configuration
        self.task_routing = {
            LLMTask.EXTRACT_EVENTS: LLMProvider.OPENAI,  # GPT-4 best for structured extraction
            LLMTask.CLASSIFY_CATEGORY: LLMProvider.ANTHROPIC,  # Claude best for reasoning
            LLMTask.ENHANCE_DESCRIPTION: LLMProvider.GOOGLE,  # Gemini good for creative text
            LLMTask.TECH_RELEVANCE: LLMProvider.GROQ,  # Fast & cheap for binary classification
            LLMTask.VALIDATE_DATA: LLMProvider.OPENAI,  # GPT-3.5 for simple validation
            LLMTask.EXTRACT_TAGS: LLMProvider.OPENAI,  # GPT-4 for structured output
            LLMTask.SUMMARIZE: LLMProvider.ANTHROPIC,  # Claude for summarization
        }
    
    def _initialize_providers(self):
        """Initialize all available LLM providers"""
        
        # OpenAI (GPT-4, GPT-3.5)
        try:
            import openai
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.providers[LLMProvider.OPENAI] = {
                    'client': openai.OpenAI(api_key=openai_key),
                    'models': {
                        'fast': 'gpt-3.5-turbo',
                        'smart': 'gpt-4-turbo',
                        'vision': 'gpt-4-vision-preview'
                    }
                }
                self.logger.info("✅ OpenAI initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ OpenAI not available: {e}")
        
        # Anthropic (Claude)
        try:
            import anthropic
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.providers[LLMProvider.ANTHROPIC] = {
                    'client': anthropic.Anthropic(api_key=anthropic_key),
                    'models': {
                        'fast': 'claude-3-haiku-20240307',
                        'smart': 'claude-3-5-sonnet-20241022'
                    }
                }
                self.logger.info("✅ Anthropic (Claude) initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ Anthropic not available: {e}")
        
        # Google (Gemini)
        try:
            import google.generativeai as genai
            google_key = os.getenv('GOOGLE_API_KEY')
            if google_key:
                genai.configure(api_key=google_key)
                self.providers[LLMProvider.GOOGLE] = {
                    'client': genai,
                    'models': {
                        'fast': 'gemini-1.5-flash',
                        'smart': 'gemini-1.5-pro'
                    }
                }
                self.logger.info("✅ Google (Gemini) initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ Google Gemini not available: {e}")
        
        # Groq (Fast inference)
        try:
            from groq import Groq
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                self.providers[LLMProvider.GROQ] = {
                    'client': Groq(api_key=groq_key),
                    'models': {
                        'fast': 'llama-3.1-8b-instant',
                        'smart': 'llama-3.1-70b-versatile'
                    }
                }
                self.logger.info("✅ Groq initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ Groq not available: {e}")
    
    def extract_events_from_html(self, html: str, source: str) -> List[Dict[str, Any]]:
        """
        Extract structured event data from HTML using LLM
        
        Args:
            html: Raw HTML content
            source: Source name (luma, partiful, etc.)
            
        Returns:
            List of extracted events
        """
        task = LLMTask.EXTRACT_EVENTS
        provider = self.task_routing.get(task, LLMProvider.OPENAI)
        
        if provider not in self.providers:
            self.logger.error(f"Provider {provider} not available for {task}")
            return []
        
        prompt = f"""Extract all events from this {source} HTML page.

Return a JSON array of events with these fields:
- title (string, required)
- description (string, extract if available)
- start_time (string, ISO format if date/time found, otherwise empty)
- end_time (string, ISO format if found)
- url (string, full event URL)
- venue_name (string, physical location if mentioned)
- organizer_name (string, if mentioned)
- tags (array of strings, extract relevant keywords)

HTML (first 30000 chars):
{html[:30000]}

Return ONLY a JSON array, no other text."""

        try:
            if provider == LLMProvider.OPENAI:
                response = self.providers[provider]['client'].chat.completions.create(
                    model=self.providers[provider]['models']['smart'],
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0
                )
                result = json.loads(response.choices[0].message.content)
                events = result.get('events', []) if isinstance(result, dict) else result
                
            elif provider == LLMProvider.ANTHROPIC:
                response = self.providers[provider]['client'].messages.create(
                    model=self.providers[provider]['models']['smart'],
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
                events = json.loads(response.content[0].text)
            
            else:
                events = []
            
            self.logger.info(f"Extracted {len(events)} events using {provider.value}")
            return events
            
        except Exception as e:
            self.logger.error(f"Event extraction failed: {e}")
            return []
    
    def classify_event_category(self, title: str, description: str) -> str:
        """
        Classify event into specific category using Claude
        
        Args:
            title: Event title
            description: Event description
            
        Returns:
            Category name
        """
        provider = LLMProvider.ANTHROPIC
        
        if provider not in self.providers:
            provider = LLMProvider.OPENAI  # Fallback
        
        prompt = f"""Classify this event into ONE of these categories:
- ai_ml (AI, Machine Learning, Deep Learning)
- data_science (Data Science, Analytics, Big Data)
- web_dev (Web Development, Frontend, Backend)
- mobile (Mobile Development, iOS, Android)
- devops (DevOps, Cloud, Kubernetes, Docker)
- blockchain (Blockchain, Crypto, Web3)
- security (Cybersecurity, InfoSec)
- startup (Startup, Entrepreneurship, VC)
- networking (Professional networking, career)
- hackathon (Hackathons, coding competitions)
- workshop (Workshops, tutorials, training)
- conference (Conferences, summits)
- other (anything else)

Event:
Title: {title}
Description: {description[:500]}

Return ONLY the category name, nothing else."""

        try:
            if provider == LLMProvider.ANTHROPIC:
                response = self.providers[provider]['client'].messages.create(
                    model=self.providers[provider]['models']['smart'],
                    max_tokens=50,
                    messages=[{"role": "user", "content": prompt}]
                )
                category = response.content[0].text.strip().lower()
            else:
                response = self.providers[provider]['client'].chat.completions.create(
                    model=self.providers[provider]['models']['fast'],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=50
                )
                category = response.choices[0].message.content.strip().lower()
            
            return category
            
        except Exception as e:
            self.logger.error(f"Category classification failed: {e}")
            return "other"
    
    def enhance_description(self, title: str, raw_description: str) -> str:
        """
        Enhance event description using Gemini
        
        Args:
            title: Event title
            raw_description: Raw/incomplete description
            
        Returns:
            Enhanced description
        """
        provider = LLMProvider.GOOGLE
        
        if provider not in self.providers:
            return raw_description  # Return original if Gemini unavailable
        
        if not raw_description or len(raw_description) < 20:
            return raw_description
        
        prompt = f"""Enhance this event description to be more informative and engaging.
Keep it concise (2-3 sentences). Focus on what attendees will learn/do.

Event: {title}
Raw description: {raw_description}

Enhanced description:"""

        try:
            model = self.providers[provider]['client'].GenerativeModel(
                self.providers[provider]['models']['fast']
            )
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Description enhancement failed: {e}")
            return raw_description
    
    def check_tech_relevance(self, title: str, description: str) -> Dict[str, Any]:
        """
        Check if event is tech-related using fast LLM (Groq/Llama)
        
        Args:
            title: Event title
            description: Event description
            
        Returns:
            Dict with is_tech_related (bool) and confidence (float)
        """
        provider = LLMProvider.GROQ
        
        if provider not in self.providers:
            provider = LLMProvider.OPENAI  # Fallback
        
        prompt = f"""Is this event related to technology/tech industry?

Event:
Title: {title}
Description: {description[:300]}

Answer in JSON format:
{{"is_tech_related": true/false, "confidence": 0.0-1.0, "reason": "brief reason"}}"""

        try:
            if provider == LLMProvider.GROQ:
                response = self.providers[provider]['client'].chat.completions.create(
                    model=self.providers[provider]['models']['fast'],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=100
                )
                result = json.loads(response.choices[0].message.content)
            else:
                response = self.providers[provider]['client'].chat.completions.create(
                    model=self.providers[provider]['models']['fast'],
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0
                )
                result = json.loads(response.choices[0].message.content)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tech relevance check failed: {e}")
            return {"is_tech_related": False, "confidence": 0.0, "reason": "error"}
    
    def extract_tags(self, title: str, description: str) -> List[str]:
        """
        Extract relevant tags from event using GPT-4
        
        Args:
            title: Event title
            description: Event description
            
        Returns:
            List of tags
        """
        provider = LLMProvider.OPENAI
        
        if provider not in self.providers:
            return []
        
        prompt = f"""Extract 5-10 relevant tags/keywords from this event.

Event:
Title: {title}
Description: {description[:500]}

Return as JSON array of strings: ["tag1", "tag2", ...]"""

        try:
            response = self.providers[provider]['client'].chat.completions.create(
                model=self.providers[provider]['models']['fast'],
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=200
            )
            result = json.loads(response.choices[0].message.content)
            tags = result.get('tags', [])
            return tags[:10]  # Limit to 10
            
        except Exception as e:
            self.logger.error(f"Tag extraction failed: {e}")
            return []
    
    def validate_event_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and correct event data using LLM
        
        Args:
            event: Event dictionary
            
        Returns:
            Dict with validation results and corrections
        """
        provider = LLMProvider.OPENAI
        
        if provider not in self.providers:
            return {"valid": True, "corrections": []}
        
        prompt = f"""Validate this event data and suggest corrections if needed:

Event: {json.dumps(event, indent=2)}

Check for:
1. Date format (should be ISO)
2. Missing required fields (title, start_time, url)
3. Inconsistencies (end_time before start_time)
4. Data quality issues

Return JSON:
{{"valid": true/false, "corrections": ["list of issues found"], "fixed_data": {{corrected fields}}}}"""

        try:
            response = self.providers[provider]['client'].chat.completions.create(
                model=self.providers[provider]['models']['fast'],
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Data validation failed: {e}")
            return {"valid": True, "corrections": []}
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return [p.value for p in self.providers.keys()]
    
    def get_provider_for_task(self, task: LLMTask) -> str:
        """Get which provider is used for a specific task"""
        return self.task_routing.get(task, LLMProvider.OPENAI).value


# Example usage
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    manager = LLMManager()
    print(f"\n🤖 Available LLM Providers: {manager.get_available_providers()}\n")
    
    # Test extraction
    sample_html = """
    <div class="event">
        <h2>AI Workshop: Build Your First LLM App</h2>
        <p>Learn to build AI applications using GPT-4</p>
        <time>2025-10-20 18:00</time>
        <span class="venue">Tech Hub NYC</span>
    </div>
    """
    
    events = manager.extract_events_from_html(sample_html, "sample")
    print(f"Extracted events: {json.dumps(events, indent=2)}")

