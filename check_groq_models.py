import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

try:
    print("Listing Groq models...")
    models = client.models.list()
    with open("groq_models.txt", "w") as f:
        for m in models.data:
            if "llama" in m.id:
                f.write(m.id + "\n")
except Exception as e:
    print(f"Error: {e}")
