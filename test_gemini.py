import os
from dotenv import load_dotenv
from google import genai

load_dotenv("backend/.env")

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEYS")

if not api_key:
    print("ERROR: Gemini API key not found")
    raise SystemExit(1)

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Reply with only: Gemini connection successful"
    )
    print("SUCCESS:", response.text)

except Exception as error:
    print("GEMINI ERROR:", error)