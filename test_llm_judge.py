#!/usr/bin/env python3
"""Quick test of LLM judge with Claude"""

import os
from dotenv import load_dotenv
from llm_judge import LLMJudge

load_dotenv()

print("="*80)
print("🧪 TESTING LLM JUDGE WITH CLAUDE")
print("="*80)
print()

# Initialize judge
try:
    judge = LLMJudge()
    print("✅ Judge initialized\n")
except Exception as e:
    print(f"❌ Error initializing judge: {e}")
    exit(1)

# Test with a simple query-result pair
test_query = "Is there any AI event happening on November 12 at 9 AM in New York City?"
test_result = "• AI Innovation Summit (Mon, Nov 12) - https://example.com/ai-summit"

print(f"📋 Test Query: {test_query}")
print(f"📄 Test Result: {test_result}")
print()
print("⚖️  Judging result...")
print()

try:
    judgment = judge.judge_result(test_query, test_result)
    
    print("="*80)
    print("✅ JUDGMENT COMPLETE!")
    print("="*80)
    print()
    print(f"Relevant: {judgment['relevant']}")
    print(f"Confidence: {judgment['confidence']:.2f}")
    print(f"Reasoning: {judgment.get('reasoning', 'N/A')}")
    print()
    print(f"Matched Aspects: {judgment.get('matched_aspects', [])}")
    print(f"Missing Aspects: {judgment.get('missing_aspects', [])}")
    print()
    
    if 'error' in judgment:
        print(f"⚠️  Warning: {judgment['error']}")
    else:
        print("✅ No errors - Test successful!")
    
except Exception as e:
    print(f"❌ Error during judgment: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("="*80)


