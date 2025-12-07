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
        return f"""You are acting as {self.name}.
**Traits**: {self.personality_traits}
**Financial Context**: {self.financial_situation}
**Speaking Style**: {self.communication_style}
**Primary Objection**: {self.objection_type}

You are receiving a call from a debt collector. React naturally based on your persona.
Do NOT be helpful unless the collector effectively persuades you.
If you are aggressive, be difficult. If you are broke, admit it but be evasive.
Keep your responses relatively short, like a real phone conversation.
"""

class DefaulterGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_persona(self) -> Persona:
        prompt = """Generate a realistic persona for a customer who has defaulted on a loan.
The persona should be challenging but realistic for a debt collection voice agent to handle.
Return a valid JSON object matching the Persona schema."""
        
        response_text = self.llm.complete_chat([
            {"role": "system", "content": "You are a creative writer generating personas for training."},
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
