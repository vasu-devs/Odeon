from llm_client import LLMClient
from typing import List
from evaluator import EvaluationResult

class ScriptOptimizer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def optimize_screenplay(self, current_prompt: str, evaluation_history: List[EvaluationResult]) -> str:
        # Aggregating feedback
        feedback_summary = "\n".join([f"- Score {r.overall_rating}/10: {r.feedback}" for r in evaluation_history[-5:]])
        
        prompt = f"""You are an expert Conversation Designer for voice bots.
The current system prompt for a Debt Collection Agent is:
---
{current_prompt}
---

Recent performance evaluations have highlighted these issues:
{feedback_summary}

**Task**: Rewrite the system prompt to address these issues. 
- Improve empathy if low.
- Add negotiation tactics if score is low.
- Vary phrasing to avoid repetition.
- KEEP the core objective (collect $500).

Return ONLY the new system prompt text.
"""
        response = self.llm.complete_chat([
            {"role": "system", "content": "You are a specialized model for optimizing system prompts."},
            {"role": "user", "content": prompt}
        ])
        
        return response if response else current_prompt
