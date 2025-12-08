from llm_client import LLMClient
from typing import List
from evaluator import EvaluationResult
import json

class ScriptOptimizer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def optimize_screenplay(self, current_prompt: str, failures: List[dict], previous_success_rate: float = 0.0, target_threshold: float = 0.8) -> str:
        # Aggregating feedback from failures
        # failures is expected to be a list of dicts: {"persona": Persona, "result": EvaluationResult, "logs": list}
        
        failure_summaries = []
        for f in failures:
            persona_name = f['persona'].name
            score = f['result'].overall_rating
            feedback = f['result'].feedback
            failure_summaries.append(f"- **{persona_name}** (Score: {score}/10): {feedback}")
        
        feedback_block = "\n".join(failure_summaries)
        
        prompt = f"""You are an expert Voice AI Architect for Fintech. Your goal is to refine the Agent System Prompt based on a BATCH of validation failures.

**INPUT DATA:**
- **Current System Prompt:**
{current_prompt}

- **Test Suite Failures (The following scenarios FAILED):**
{feedback_block}

- **Success Metrics:**
  - Current Rate: {previous_success_rate:.1%}
  - Target Rate: {target_threshold:.1%}

**TASK:**
Analyze the common patterns in these failures. Did the agent fail to carry context? Did it hallucinates math? Was it too rude?

Your goal is to achieve a success rate of {target_threshold:.0%}. You do not need to achieve 100%. Focus on fixing the specific failures that prevent reaching this threshold. If the current score is close to the threshold, make minor adjustments. If it is far, make major adjustments.

Rewrite the System Prompt to fix these specific weaknesses while ensuring it doesn't break for other scenarios.

**CRITICAL RULES FOR THE NEW PROMPT:**
1. **NO DYNAMIC MATH:** Do not calculate interest or fees. Debt is fixed.
2. **NO FALSE PROMISES:** No debt forgiveness.
3. **JSON SAFETY:** Scores must be integers.
4. **VOICE FLOW:** Keep it concise (max 2 sentences).
5. **STRICT OPTIMIZATION:** { "We are underperforming. IMPROVE ADAPTABILITY." if previous_success_rate < target_threshold else "We are matching/exceeding expectations. CONSOLIDATE AND PREVENT REGRESSION." }

**OUTPUT:**
Generate the full, executable System Prompt only.
"""
        response = self.llm.complete_chat([
            {"role": "system", "content": "You are a specialized model for optimizing system prompts."},
            {"role": "user", "content": prompt}
        ])
        
        return response if response else current_prompt
