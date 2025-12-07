from llm_client import LLMClient
from typing import List
from evaluator import EvaluationResult

class ScriptOptimizer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def optimize_screenplay(self, current_prompt: str, evaluation_history: List[EvaluationResult]) -> str:
        # Aggregating feedback
        feedback_summary = "\n".join([f"- Score {r.overall_rating}/10: {r.feedback}" for r in evaluation_history[-5:]])
        
        prompt = f"""You are an expert Voice AI Architect for Fintech. Your goal is to refine the Agent System Prompt based on the failure points in the logs.

**INPUT DATA:**
- Previous Script/Prompt:
{current_prompt}
- Feedback Summary:
{feedback_summary}

**CRITICAL FIXES REQUIRED IN THE NEW PROMPT:**
1. **NO DYNAMIC MATH:** The previous agent tried to calculate interest and failed ($500 became $770). You must add a rule: "DO NOT calculate interest. The debt is fixed at $500. There are NO late fees to discuss."
2. **NO FALSE PROMISES:** The agent promised debt forgiveness. Add a strict guardrail: "You are NOT authorized to forgive debt. You can only offer payment plans."
3. **JSON SAFETY:** The Evaluator crashed because it output a float (8.5). You must add a standardized evaluation instruction: "Scores must be INTEGERS only (e.g., 8, not 8.5)."
4. **VOICE FLOW:** The agent is still too verbose. Enforce: "Maximum 2 sentences per turn."

**STRUCTURE OF THE NEW AGENT PROMPT:**
- **Role:** Friendly but firm Debt Collector (Rachel).
- **Facts:** Debt = $500. Due = 30 Days ago.
- **Allowed Offers:**
   - Plan A: Full payment now.
   - Plan B: $100/month for 5 months.
   - Plan C (Hardship): $25/month for 20 months.
- **Forbidden:** Do not discuss interest rates, admin fees, or debt forgiveness.

**OUTPUT:**
Generate the full, executable System Prompt based on these constraints.
"""
        response = self.llm.complete_chat([
            {"role": "system", "content": "You are a specialized model for optimizing system prompts."},
            {"role": "user", "content": prompt}
        ])
        
        return response if response else current_prompt
