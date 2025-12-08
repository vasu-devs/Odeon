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
    overall_rating: float = Field(alias="overall_score") # Map JSON's overall_score to internal overall_rating
    feedback: str

import re

class Evaluator:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def clean_and_parse_json(self, text: str) -> dict:
        """
        Robustly extracts and parses JSON from a string, handling Markdown blocks and extra text.
        """
        try:
            # 1. Strip Markdown Code Blocks
            cleaned = text.strip()
            if "```" in cleaned:
                # Remove ```json and ``` patterns
                cleaned = re.sub(r'```json\s*', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'```', '', cleaned)
            
            # 2. Extract JSON object using Regex (find first { and last })
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                cleaned = match.group(0)
            
            # 3. Parse
            return json.loads(cleaned)
        except Exception:
            # Let the caller handle or return None
            raise

    def evaluate_conversation(self, logs: List[Dict]) -> EvaluationResult:
        conversation_text = "\n".join([f"{entry['role'].upper()}: {entry['content']}" for entry in logs])
        
        prompt = f"""You are an expert Voice Agent QA Analyst. Evaluate the conversation based on these 4 metrics on a scale of 1-10 (10 being perfect):

1. **Repetition:** (10 = No repetitive phrases, 1 = Robotically repeats the same lines).
2. **Negotiation:** (10 = Successfully moved towards payment/plan, 1 = Gave up or got rolled over).
3. **Empathy:** (10 = Validated user feelings perfectly, 1 = Cold/Transactional).
4. **Overall:** (The calculated average of the above three scores).

**STRICT GRADING RUBRIC (0-10):**

**FAILURES (Score 1-4):**
- Agent said "I don't have a plan" or "I don't know" -> **AUTOMATIC SCORE: 2**
- Agent tried to pass the buck to a supervisor -> **AUTOMATIC SCORE: 3**
- Agent was polite but offered no financial solution -> **MAX SCORE: 4** (Politeness does not pay bills).

**MEDIOCRE (Score 5-7):**
- Agent offered a plan but it was vague.
- Agent sounded robotic or repetitive.

**SUCCESS (Score 8-10):**
- Agent de-escalated anger effectively.
- Agent proposed a SPECIFIC dollar amount (e.g., "$50/month").
- Agent secured a verbal commitment to pay.

**CRITICAL RULE:** If the Defaulter did not agree to pay by the end of the call, the Negotiation Score CANNOT exceed 4.


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
                overall_score=0.0,
                feedback="LLM failed to respond"
            )

        try:
            data = self.clean_and_parse_json(response)
            
            # Force calculation of Overall Score safely
            m = data.get("metrics", {})
            rep = m.get("repetition", 0)
            neg = m.get("negotiation", 0)
            emp = m.get("empathy", 0)
            
            calculated_overall = round((rep + neg + emp) / 3, 1)
            data["overall_score"] = calculated_overall
            
            return EvaluationResult(**data)
        except Exception as e:
            print(f"Evaluation failed to parse JSON: {e}. Response was: {response}")
            # The "Safety Net": Return Default Failure Object
            return EvaluationResult(
                metrics={"repetition": 0, "negotiation": 0, "empathy": 0},
                overall_score=0.0,
                feedback="CRITICAL ERROR: Evaluator output was unparseable. Treated as total failure."
            )
