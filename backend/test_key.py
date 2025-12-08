import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Key loaded: {api_key[:5]}...{api_key[-4:] if api_key else 'None'}")

genai.configure(api_key=api_key)

model_name = "gemini-1.5-flash"
print(f"Testing {model_name}...")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say Hello")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"FAIL: {e}")
