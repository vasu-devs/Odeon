from dotenv import load_dotenv
import os
from llm_client import LLMClient
from agent import DebtCollectionAgent

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = LLMClient(provider="groq", api_key=api_key, model_name="llama-3.3-70b-versatile")
agent = DebtCollectionAgent(client)

print("-"*20)
print("Testing Agent Response...")
# Initial greeting is already in system prompt or inferred, but let's just trigger a response.
# The agent usually starts.
print(f"System Prompt Head:\n{agent.system_prompt[:200]}...")

# Simulate a user saying hello
response = agent.respond("Hello?")
print(f"Agent Response: {response}")

if "Turn 1" in response or "**Response" in response:
    print("FAIL: Found artifacts.")
else:
    print("PASS: Output looks clean.")
print("-"*20)
