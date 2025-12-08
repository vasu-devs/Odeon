from llm_client import LLMClient
from typing import List
from evaluator import EvaluationResult
import json

class ScriptOptimizer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def optimize_screenplay(self, current_prompt: str, failures: List[dict], previous_success_rate: float = 0.0, target_thresholds: dict = None) -> str:
        
        # 1. Safe Threshold Extraction (Fixes the NameError bug)
        # Handle if target_thresholds is a Pydantic object or a Dict
        if hasattr(target_thresholds, 'dict'):
            targets = target_thresholds.dict()
            overall_target = target_thresholds.overall
        elif isinstance(target_thresholds, dict):
            targets = target_thresholds
            overall_target = targets.get('overall', 0.8)
        else:
            # Fallback defaults
            targets = {"repetition": 8, "negotiation": 8, "empathy": 8, "overall": 8}
            overall_target = 0.8

        # 2. Build Failure Summaries
        failure_summaries = []
        for f in failures:
            persona_name = f['persona'].get('name', 'Unknown')
            # Handle if result is dict or object
            result = f['result']
            if hasattr(result, 'metrics'):
                metrics = result.metrics
                score = result.overall_rating
                feedback = result.feedback
                # Access Pydantic fields
                m_rep = metrics.repetition
                m_neg = metrics.negotiation
                m_emp = metrics.empathy
            else:
                # Handle dict case
                m_rep = result.get('metrics', {}).get('repetition', 0)
                m_neg = result.get('metrics', {}).get('negotiation', 0)
                m_emp = result.get('metrics', {}).get('empathy', 0)
                score = result.get('overall_score', 0)
                feedback = result.get('feedback', '')

            # Identify specific gaps
            gaps = []
            if m_rep < targets['repetition']: gaps.append(f"Repetition ({m_rep} < {targets['repetition']})")
            if m_neg < targets['negotiation']: gaps.append(f"Negotiation ({m_neg} < {targets['negotiation']})")
            if m_emp < targets['empathy']: gaps.append(f"Empathy ({m_emp} < {targets['empathy']})")
            
            failure_summaries.append(f"- **Scenario: {persona_name}** | Gaps: {', '.join(gaps)} | Feedback: {feedback}")

        feedback_block = "\n".join(failure_summaries)
        targets_str = ", ".join([f"{k.capitalize()}: {v}" for k,v in targets.items()])

        # 3. The "S-Tier" Prompt
        prompt = f"""You are a Lead Conversation Designer and AI Architect.
Your task is to REWRITE an AI System Prompt to fix specific behavioral failures observed in testing.

**CONTEXT:**
We are training a Debt Collection Voice Agent.
- Current Success Rate: {previous_success_rate:.1%}
- Target Success Rate: {overall_target:.1%}
- Target Metrics: {targets_str}

**INPUT DATA:**
--- CURRENT SYSTEM PROMPT ---
{current_prompt}
-----------------------------

--- FAILED TEST CASES ---
{feedback_block}
-------------------------

**DIAGNOSTIC PROTOCOL (Mental Sandbox):**
1. Analyze the failures. Did the Agent freeze? Did it get angry? Did it lack a plan?
2. Map failures to specific fixes:
   - **Low Negotiation:** The Agent likely lacked specific numbers/authority. -> *Action: Add specific authorized offers (e.g., "$50/mo").*
   - **Low Empathy:** The Agent ignored the user's struggle. -> *Action: Add a rule to "Always validate hardship before asking for money".*
   - **Low Repetition:** The Agent repeated the same phrase. -> *Action: Add a rule to "Vary responses".*
   - **"No Plan":** The Agent said "I don't know". -> *Action: Explicitly provide policy details (Company Name, PO Box, Interest Rate).*

**INSTRUCTIONS FOR REWRITING:**
Rewrite the `CURRENT SYSTEM PROMPT` to fix these issues.

**CRITICAL CONSTRAINT CHECKLIST:**
1. **PRESERVE SAFETY:** Do NOT remove the `CRITICAL OUTPUT RULES` (No headers, no markdown) at the top.
2. **ANTI-HALLUCINATION:** Keep the "Strict Constraints" but MODIFY them to allow specific authorized actions (like offering a payment plan).
3. **XML HYGIENE:** Use strictly valid XML tags. 
   - CORRECT: `<instructions>...</instructions>`
   - WRONG: `<instructions...` or `</instructionsinstructions>`
4. **NO DYNAMIC MATH:** Hardcode all numbers.

**OUTPUT:**
Return ONLY the full, refined System Prompt. Do not include explanation or markdown backticks.
"""

        response = await self.llm.complete_chat([
            {"role": "system", "content": "You are an expert prompt engineer. You output only raw text prompt files."},
            {"role": "user", "content": prompt}
        ])
        
        # Fallback if LLM fails
        return response if response else current_prompt