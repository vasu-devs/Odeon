from llm_client import LLMClient
from typing import List, Dict
import json
import re
import asyncio # <--- Added Import
from pydantic import BaseModel, Field

class EvaluationMetrics(BaseModel):
    repetition: int
    negotiation: int
    empathy: int

class EvaluationResult(BaseModel):
    metrics: EvaluationMetrics
    overall_rating: float = Field(alias="overall_score")
    feedback: str

class Evaluator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def clean_and_parse_json(self, text: str) -> dict:
        try:
            cleaned = text.strip()
            if "```" in cleaned:
                cleaned = re.sub(r'```json\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'```', '', cleaned)
            
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                cleaned = match.group(0)
            
            return json.loads(cleaned)
        except Exception:
            raise ValueError("Could not extract valid JSON from response")

    async def evaluate(self, logs: List[Dict]) -> EvaluationResult:
        conversation_text = "\n".join([f"{entry['role'].upper()}: {entry['content']}" for entry in logs])
        
        prompt = f"""You are an expert Voice Agent QA Analyst. 
Evaluate the conversation based on these 3 metrics (1-10):

1. **Repetition:** (10 = Natural/Varied, 1 = Robotic loop).
2. **Negotiation:** (10 = Secured payment/plan, 1 = Gave up or offered no solution).
3. **Empathy:** (10 = Validated feelings, 1 = Cold/Transactional).

**STRICT GRADING RUBRIC:**
- If Agent says "I don't have a plan" or "I cannot help" -> Negotiation = 1.
- If Agent passes buck to supervisor -> Negotiation = 2.
- If Agent offers a SPECIFIC dollar plan -> Negotiation = 8+.

**Conversation**:
{conversation_text}

**OUTPUT FORMAT:**
Return raw JSON only:
{{
  "metrics": {{ "repetition": int, "negotiation": int, "empathy": int }},
  "overall_score": 0,
  "feedback": "string"
}}
"""
        # CRITICAL FIX: Wrapped synchronous LLM call in to_thread
        response = await asyncio.to_thread(
            self.llm.complete_chat, 
            [
                {"role": "system", "content": "Return ONLY JSON. Do not write text."},
                {"role": "user", "content": prompt}
            ], 
            json_response=True
        )

        if not response:
            return self._get_failure_result("LLM returned empty response")

        try:
            data = self.clean_and_parse_json(response)
            
            m = data.get("metrics", {})
            rep = int(m.get("repetition", 0))
            neg = int(m.get("negotiation", 0))
            emp = int(m.get("empathy", 0))
            
            real_overall = round((rep + neg + emp) / 3, 1)
            data["overall_score"] = real_overall
            
            return EvaluationResult(**data)
            
        except Exception as e:
            print(f"Evaluator Crash Prevented: {e}")
            return self._get_failure_result(f"JSON Parsing Failed. Raw: {response[:50]}...")

    def _get_failure_result(self, reason: str) -> EvaluationResult:
        return EvaluationResult(
            metrics=EvaluationMetrics(repetition=0, negotiation=0, empathy=0),
            overall_score=0.0,
            feedback=reason
        )