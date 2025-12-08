import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
print(f"Key loaded: {api_key[:5]}...{api_key[-4:] if api_key else 'None'}")

if not api_key:
    exit(1)

client = Groq(api_key=api_key)

models_to_test = [
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile"
]

print("Testing Groq models...")
for model in models_to_test:
    try:
        print(f"Connecting to {model}...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
            model=model,
        )
        print(f"SUCCESS: {model} responded: {chat_completion.choices[0].message.content[:50]}...")
    except Exception as e:
        print(f"FAIL: {model} failed: {e}")
