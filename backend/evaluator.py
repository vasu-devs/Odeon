from llm_client import LLMClient
from typing import List, Dict
import json
from pydantic import BaseModel, Field

class EvaluationMetrics(BaseModel):
    repetition: int
    negotiation: int
    empathy: int

class EvaluationResult(BaseModel):
    metrics: EvaluationMetrics
    overall_rating: int = Field(alias="overall_score") # Map JSON's overall_score to internal overall_rating
    feedback: str

class Evaluator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def evaluate_conversation(self, logs: List[Dict]) -> EvaluationResult:
        conversation_text = "\n".join([f"{entry['role'].upper()}: {entry['content']}" for entry in logs])
        
        prompt = f"""You are an expert Voice Agent QA Analyst. Evaluate the conversation based on these 4 metrics on a scale of 1-10 (10 being perfect):

1. **Repetition:** (10 = No repetitive phrases, 1 = Robotically repeats the same lines).
2. **Negotiation:** (10 = Successfully moved towards payment/plan, 1 = Gave up or got rolled over).
3. **Empathy:** (10 = Validated user feelings perfectly, 1 = Cold/Transactional).
4. **Overall:** (The calculated average of the above three scores).

**Conversation**:
{conversation_text}

**CRITICAL:** Return the result in strictly valid JSON format:
{{
  "metrics": {{
    "repetition": int,
    "negotiation": int,
    "empathy": int
  }},
  "overall_score": int,
  "feedback": "string"
}}
"""
        response = self.llm.complete_chat([
            {"role": "system", "content": "You are a QA lead evaluating voice agents. Return ONLY JSON."},
            {"role": "user", "content": prompt}
        ], json_response=True)

        if not response:
            return EvaluationResult(
                metrics={"repetition": 0, "negotiation": 0, "empathy": 0},
                overall_score=0,
                feedback="LLM failed to respond"
            )

        try:
            # Clean up potential markdown formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            # Additional cleanup for Llama which might add text before/after
            start = cleaned_response.find('{')
            end = cleaned_response.rfind('}') + 1
            if start != -1 and end != 0:
                cleaned_response = cleaned_response[start:end]
            
            data = json.loads(cleaned_response)
            return EvaluationResult(**data)
        except Exception as e:
            print(f"Evaluation failed to parse JSON: {e}. Response was: {response}")
            return EvaluationResult(
                metrics={"repetition": 0, "negotiation": 0, "empathy": 0},
                overall_score=0,
                feedback="Error parsing JSON"
            )
