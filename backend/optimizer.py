from llm_client import LLMClient
from typing import List, Union
import asyncio

class ScriptOptimizer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def optimize_screenplay(self, current_prompt: str, failures: List[dict], previous_success_rate: float = 0.0, target_thresholds: Union[dict, object] = None) -> str:
        
        # 1. Safe Threshold Extraction
        if hasattr(target_thresholds, 'dict'):
            targets = target_thresholds.dict()
            overall_target = target_thresholds.overall
        elif isinstance(target_thresholds, dict):
            targets = target_thresholds
            overall_target = targets.get('overall', 0.8)
        else:
            targets = {"repetition": 8, "negotiation": 8, "empathy": 8}
            overall_target = 0.8

        # 2. Build Rich Failure Context
        failure_summaries = []
        for f in failures:
            # FIX: Handle Persona Pydantic Object vs Dict
            p_obj = f.get('persona')
            if hasattr(p_obj, 'name'):
                persona_name = p_obj.name
            else:
                persona_name = p_obj.get('name', 'Unknown') if isinstance(p_obj, dict) else 'Unknown'

            res = f.get('result')
            
            # FIX: Handle EvaluationResult Pydantic Object vs Dict
            if hasattr(res, 'metrics'):
                m = res.metrics
                feedback = res.feedback
                scores = f"Rep:{m.repetition} Neg:{m.negotiation} Emp:{m.empathy}"
            else:
                m = res.get('metrics', {})
                feedback = res.get('feedback', '')
                scores = f"Rep:{m.get('repetition')} Neg:{m.get('negotiation')}"

            failure_summaries.append(f"- **{persona_name}** [{scores}]: {feedback}")

        feedback_block = "\n".join(failure_summaries)
        
        # 3. Prompt Construction
        prompt = f"""You are a Lead AI Architect. REWRITE the System Prompt to fix behavioral failures.

**CONTEXT:**
- Current Success: {previous_success_rate:.1%} (Target: {overall_target:.1%})
- Target Metrics: {targets}

**INPUT:**
--- CURRENT PROMPT ---
{current_prompt}
----------------------
--- FAILED SCENARIOS ---
{feedback_block}
------------------------

**DIAGNOSTIC:**
1. If Negotiation is low: The Agent likely lacked specific payment options ($/mo). -> *Action: Add specific payment plans.*
2. If Empathy is low: The Agent ignored hardship. -> *Action: Add validation rules.*
3. If "No Plan": The Agent refused to help. -> *Action: Authorize specific negotiation tactics.*

**INSTRUCTIONS:**
Rewrite the `CURRENT PROMPT`. 
- **PRESERVE SAFETY:** Keep the "CRITICAL OUTPUT RULES" (No headers).
- **ANTI-HALLUCINATION:** Keep the constraints, but ADD specific authorized plans to the `<user_instructions>`.
- **XML HYGIENE:** Ensure tags like `<strict_constraints>` are properly closed.
- Ensure the new prompt is **SIMPLE** text. Do not over-engineer the XML structure.

**OUTPUT:**
Return ONLY the full, executable System Prompt. No markdown.
"""

        # CRITICAL FIX: Wrapped synchronous LLM call in to_thread
        # This prevents "object str can't be used in 'await'" and "coroutine not iterable" errors
        response = await asyncio.to_thread(
            self.llm.complete_chat,
            [
                {"role": "system", "content": "You are a prompt engineer. Output raw text only."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response if response else current_prompt