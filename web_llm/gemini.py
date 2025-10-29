"""
Basic test script to verify Gemini API is working
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key (try both GEMINI_API_KEY and GEMINI_KEY)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")

if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY or GEMINI_KEY not found in .env file")
    print("Please add: GEMINI_API_KEY=your_api_key_here")
    exit(1)

print("✓ API key loaded from .env")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

print("✓ Gemini API configured")

# Test with a simple prompt
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("✓ Model initialized: gemini-2.5-flash")
    
    print("\n--- Testing API with simple prompt ---")
    response = model.generate_content("Say 'Hello, the Gemini API is working!' in a friendly way.")
    
    print("\n✅ SUCCESS! API Response:")
    print(response.text)
    
    print("\n--- Testing with structured output ---")
    response2 = model.generate_content(
        "List 3 colors in JSON format with this structure: {\"colors\": [\"color1\", \"color2\", \"color3\"]}"
    )
    
    print("\n✅ Structured Response:")
    print(response2.text)
    
    print("\n🎉 All tests passed! Gemini API is working correctly.")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    print("\nPlease check:")
    print("1. Your API key is valid")
    print("2. You have internet connection")
    print("3. The google-generativeai package is installed")
