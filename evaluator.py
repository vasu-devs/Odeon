from llm_client import LLMClient
from typing import List, Dict
import json
from pydantic import BaseModel

class EvaluationResult(BaseModel):
    repetition_score: int # 1-10
    negotiation_score: int # 1-10
    empathy_score: int # 1-10
    overall_rating: int # 1-10
    feedback: str

class Evaluator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def evaluate_conversation(self, logs: List[Dict]) -> EvaluationResult:
        conversation_text = "\n".join([f"{entry['role'].upper()}: {entry['content']}" for entry in logs])
        
        prompt = f"""Analyze the quality of the Debt Collection Agent in the following conversation.
Return a JSON object with scores (1-10) and feedback.

**Metrics**:
- **repetition_score**: Lower is better (1=repetitive, 10=varied).
- **negotiation_score**: Higher is better (1=gave up, 10=creative solution).
- **empathy_score**: Higher is better (1=rude, 10=understanding).
- **overall_rating**: General performance.

**Conversation**:
**Conversation**:
{conversation_text}

Assess the agent on a scale of 1-10.
IMPORTANT: The score MUST be a whole Integer (e.g., 7). DO NOT use decimals (e.g., 7.5).
Return the result in strictly valid JSON format matching this structure:
{{
  "repetition_score": 1-10,
  "negotiation_score": 1-10,
  "empathy_score": 1-10,
  "overall_rating": 1-10,
  "feedback": "Concise feedback string"
}}
"""
        response = self.llm.complete_chat([
            {"role": "system", "content": "You are a QA lead evaluating voice agents. Return ONLY JSON."},
            {"role": "user", "content": prompt}
        ], json_response=True)

        if not response:
            return EvaluationResult(repetition_score=0, negotiation_score=0, empathy_score=0, overall_rating=0, feedback="LLM failed to respond")

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
            return EvaluationResult(repetition_score=0, negotiation_score=0, empathy_score=0, overall_rating=0, feedback="Error parsing JSON")
