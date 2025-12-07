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
{conversation_text}

Output JSON matching the EvaluationResult schema.
"""
        response = self.llm.complete_chat([
            {"role": "system", "content": "You are a QA lead evaluating voice agents."},
            {"role": "user", "content": prompt}
        ], json_response=True)

        try:
            data = json.loads(response)
            return EvaluationResult(**data)
        except Exception as e:
            print(f"Evaluation failed: {e}")
            return EvaluationResult(repetition_score=0, negotiation_score=0, empathy_score=0, overall_rating=0, feedback="Error")
