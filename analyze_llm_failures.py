"""
Analyze LLM Judge failures to identify common patterns
"""
import json
from collections import defaultdict, Counter

# Load the LLM judge results
with open('ollama_benchmark_20251030_035130_llm_judge.json', 'r') as f:
    data = json.load(f)

print("="*80)
print("FAILURE PATTERN ANALYSIS: LLM Judge Results")
print("="*80)
print()

# Track patterns
missing_aspects_counter = Counter()
disagreement_patterns = defaultdict(list)
time_failures = []
location_failures = []
date_failures = []
platform_failures = []
topic_failures = []

total_results = 0
llm_rejected = 0
constraint_accepted = 0
disagreements = 0

for query in data['queries']:
    query_id = query['query_id']
    query_text = query['query_text']
    
    for judgment in query['judgments']:
        total_results += 1
        llm_j = judgment['llm_judgment']
        const_e = judgment['constraint_evaluation']
        
        # Count disagreements
        if not judgment['agreement']:
            disagreements += 1
            
            # If LLM rejected but constraint accepted (most interesting case)
            if not llm_j['relevant'] and const_e['relevant']:
                llm_rejected += 1
                constraint_accepted += 1
                
                # Analyze missing aspects
                for aspect in llm_j['missing_aspects']:
                    missing_aspects_counter[aspect] += 1
                    
                    # Categorize by failure type
                    aspect_lower = aspect.lower()
                    if any(word in aspect_lower for word in ['time', 'date', 'november', 'weekend', 'tomorrow', 'week', 'month']):
                        time_failures.append({
                            'query_id': query_id,
                            'query': query_text,
                            'title': judgment['title'],
                            'reasoning': llm_j['reasoning'],
                            'missing_aspect': aspect
                        })
                    
                    if any(word in aspect_lower for word in ['location', 'city', 'place', 'where']):
                        location_failures.append({
                            'query_id': query_id,
                            'query': query_text,
                            'title': judgment['title'],
                            'reasoning': llm_j['reasoning'],
                            'missing_aspect': aspect
                        })
                    
                    if any(word in aspect_lower for word in ['platform', 'eventbrite', 'luma', 'meetup']):
                        platform_failures.append({
                            'query_id': query_id,
                            'query': query_text,
                            'title': judgment['title'],
                            'reasoning': llm_j['reasoning'],
                            'missing_aspect': aspect
                        })

print(f"Total Results Evaluated: {total_results}")
print(f"Total Disagreements: {disagreements} ({disagreements/total_results*100:.1f}%)")
print(f"LLM Rejected but Constraint Accepted: {llm_rejected} ({llm_rejected/total_results*100:.1f}%)")
print()

print("="*80)
print("TOP MISSING ASPECTS (Why LLM Rejected Results)")
print("="*80)
for aspect, count in missing_aspects_counter.most_common(15):
    pct = count / llm_rejected * 100 if llm_rejected > 0 else 0
    print(f"{aspect:40s}: {count:3d} ({pct:5.1f}%)")
print()

print("="*80)
print("TIME/DATE FAILURES")
print("="*80)
print(f"Total time-related failures: {len(time_failures)}")
print()
if time_failures:
    print("Sample failures:")
    for i, failure in enumerate(time_failures[:5], 1):
        print(f"\n{i}. Query #{failure['query_id']}: {failure['query'][:70]}...")
        print(f"   Title: {failure['title'][:70]}...")
        print(f"   Missing: {failure['missing_aspect']}")
        print(f"   Reasoning: {failure['reasoning'][:150]}...")
print()

print("="*80)
print("LOCATION FAILURES")
print("="*80)
print(f"Total location-related failures: {len(location_failures)}")
print()
if location_failures:
    print("Sample failures:")
    for i, failure in enumerate(location_failures[:5], 1):
        print(f"\n{i}. Query #{failure['query_id']}: {failure['query'][:70]}...")
        print(f"   Title: {failure['title'][:70]}...")
        print(f"   Missing: {failure['missing_aspect']}")
        print(f"   Reasoning: {failure['reasoning'][:150]}...")
print()

print("="*80)
print("PLATFORM FAILURES")
print("="*80)
print(f"Total platform-related failures: {len(platform_failures)}")
print()
if platform_failures:
    print("Sample failures:")
    for i, failure in enumerate(platform_failures[:5], 1):
        print(f"\n{i}. Query #{failure['query_id']}: {failure['query'][:70]}...")
        print(f"   Title: {failure['title'][:70]}...")
        print(f"   Missing: {failure['missing_aspect']}")
        print(f"   Reasoning: {failure['reasoning'][:150]}...")
print()

# Analyze reasoning patterns
print("="*80)
print("COMMON REASONING PATTERNS IN DISAGREEMENTS")
print("="*80)

reasoning_keywords = defaultdict(int)
for query in data['queries']:
    for judgment in query['judgments']:
        if not judgment['agreement']:
            llm_j = judgment['llm_judgment']
            const_e = judgment['constraint_evaluation']
            
            if not llm_j['relevant'] and const_e['relevant']:
                reasoning = llm_j['reasoning'].lower()
                
                # Check for common patterns
                if 'does not' in reasoning or 'no information' in reasoning or 'not mentioned' in reasoning:
                    reasoning_keywords['Missing specific information'] += 1
                if 'past' in reasoning or 'occurred' in reasoning or 'already' in reasoning:
                    reasoning_keywords['Past events (temporal mismatch)'] += 1
                if 'general' in reasoning or 'directory' in reasoning or 'listing' in reasoning:
                    reasoning_keywords['Generic listings/directories'] += 1
                if 'landing page' in reasoning or 'overview' in reasoning:
                    reasoning_keywords['Landing pages without specifics'] += 1
                if 'date' in reasoning and ('not' in reasoning or 'missing' in reasoning):
                    reasoning_keywords['Missing/wrong date'] += 1
                if 'time' in reasoning and ('not' in reasoning or 'missing' in reasoning):
                    reasoning_keywords['Missing/wrong time'] += 1
                if 'location' in reasoning and ('not' in reasoning or 'missing' in reasoning):
                    reasoning_keywords['Missing/wrong location'] += 1

print("\nReasoning Pattern Counts:")
for pattern, count in sorted(reasoning_keywords.items(), key=lambda x: x[1], reverse=True):
    pct = count / llm_rejected * 100 if llm_rejected > 0 else 0
    print(f"{pattern:45s}: {count:3d} ({pct:5.1f}%)")
print()

# Summary
print("="*80)
print("SUMMARY: PRIMARY FAILURE CAUSES")
print("="*80)
print()
print("The LLM judge is STRICTER than constraint-based evaluation because:")
print()
print(f"1. TIME/DATE PRECISION: {len(time_failures)} failures")
print("   - LLM rejects results that don't confirm specific dates/times")
print("   - Constraint-based accepts if topic/location match, even with wrong dates")
print()
print(f"2. GENERIC LISTINGS: {reasoning_keywords.get('Generic listings/directories', 0)} failures")
print("   - LLM rejects event directories without specific actionable events")
print("   - Constraint-based accepts directories if they match topic/location")
print()
print(f"3. MISSING INFORMATION: {reasoning_keywords.get('Missing specific information', 0)} failures")
print("   - LLM requires confirmation of ALL query criteria")
print("   - Constraint-based uses partial matching")
print()
print(f"4. LOCATION: {len(location_failures)} failures")
print("   - LLM rejects if location not clearly stated or wrong")
print()
print(f"5. PLATFORM: {len(platform_failures)} failures")
print("   - LLM rejects if platform doesn't match (e.g., not on Eventbrite/Luma)")
print()
print("="*80)
