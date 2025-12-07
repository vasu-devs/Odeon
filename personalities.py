from pydantic import BaseModel, Field
from typing import List
import json
from llm_client import LLMClient

class Persona(BaseModel):
    name: str = Field(..., description="Name of the persona")
    personality_traits: str = Field(..., description="Key personality traits (e.g., Aggressive, Timid)")
    financial_situation: str = Field(..., description="Reason for default or financial context")
    communication_style: str = Field(..., description="How they speak (short, verbose, angry, polite)")
    objection_type: str = Field(..., description="Primary objection (e.g., 'I already paid', 'I have no money', 'Who are you?')")

    def to_system_prompt(self):
        return f"""You are roleplaying a specific customer persona who owes money to RiverLine Bank.
Current Persona: {self.name}
Personality Traits: {self.personality_traits}
Loan Details: $500 overdue, 30 days late.

**INSTRUCTIONS:**
- Respond naturally as a human would in a voice call.
- React emotionally to the Agent's tone. If they are rude or robotic, get angry. If they are empathetic, calm down slightly.
- **Objections:** You have excuses (lost job, medical bills, disputed debt). Make the agent work to find the truth.
- **Resolution:** Only agree to pay if the Agent offers a specific, realistic plan (e.g., small monthly installments) and treats you with respect.
- Keep responses concise (1-3 sentences) to simulate real dialogue.
"""

class DefaulterGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_persona(self) -> Persona:
        prompt = """Generate a realistic persona for a customer who has defaulted on a loan.
The persona should be challenging but realistic for a debt collection voice agent to handle.

RETURN RAW JSON ONLY. NO MARKDOWN.
Input Schema:
{
  "name": "Full Name (String)",
  "personality_traits": "Traits (String)",
  "financial_situation": "Context (String)",
  "communication_style": "Style (String)",
  "objection_type": "Objection (String)"
}
Ensure all fields are simple strings, not objects.
"""
        
        response_text = self.llm.complete_chat([
            {"role": "system", "content": "You are a creative writer generating personas for training. Output valid flat JSON only."},
            {"role": "user", "content": prompt}
        ], json_response=True)
        
        try:
            data = json.loads(response_text)
            return Persona(**data)
        except Exception as e:
            print(f"Failed to parse persona: {e}")
            # Fallback
            return Persona(
                name="John Doe", 
                personality_traits="Neutral", 
                financial_situation="Forgot to pay", 
                communication_style="Direct", 
                objection_type="Forgot"
            )

class DefaulterAgent:
    def __init__(self, persona: Persona, llm_client: LLMClient):
        self.persona = persona
        self.llm = llm_client
        self.history = [{"role": "system", "content": self.persona.to_system_prompt()}]

    def respond(self, message: str):
        self.history.append({"role": "user", "content": message})
        response = self.llm.complete_chat(self.history)
        if response:
            self.history.append({"role": "assistant", "content": response})
        return response
