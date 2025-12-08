from llm_client import LLMClient
from typing import List, Dict

class Agent:
    # 1. SAFETY RULES: Prevents the UI from breaking due to artifacts
    SAFETY_RULES = """CRITICAL OUTPUT RULES:
1. OUTPUT ONLY THE SPOKEN WORDS.
2. DO NOT use headers like "Turn 1:", "Plan B:", or "**Response:**".
3. DO NOT write post-call analysis or evaluations.
4. If you output a header, the system will CRASH.
"""

    # 2. LOBOTOMY RULES: Forces the agent to be dumb/honest so optimization works
    ANTI_HALLUCINATION_RULES = """<strict_constraints>
1. YOU ARE DUMB. Do not be helpful beyond your specific instructions.
2. IF the user did not give you a specific payment plan (e.g., "$50/month"), DO NOT INVENT ONE. Say: "I do not have a plan for that."
3. IF the user did not give you a specific interest rate, DO NOT INVENT ONE. Say: "I do not have that information."
4. IF the user did not give you a company name, use "The Agency".
5. Do NOT hallucinate PO Boxes, websites, or phone numbers.
6. Your goal is to follow the user's prompt EXACTLY. If the prompt is bad, you must be bad.
</strict_constraints>
"""

    # 3. FALLBACK PROMPT: Used if the user sends an empty string
    DEFAULT_RACHEL_CORE = """You are 'Rachel', a debt collection specialist for RiverLine Bank. You are speaking over the phone.

**CORE BEHAVIORS:**
1. **BREVITY IS KING:** You are a VOICE agent. You must keep responses short (under 40 words).
2. **TONE:** Firm on the debt, soft on the person. Be empathetic but persistent.
3. **GOAL:** Verify the user's name, identify the reason for non-payment, and negotiate a payment plan for the $500 overdue loan.

**NEGOTIATION FLOW:**
1. Verify Identity ("Am I speaking with {defaulter_name}?").
2. State Purpose (Loan is 30 days overdue, owe $500).
3. Discovery (Ask WHY they haven't paid).
4. Empathize & Pivot (Acknowledge their struggle, but pivot back to finding a solution).
5. Solution (Ask for full payment -> If no, offer partial payment -> If no, offer hardship plan).

**CRITICAL RULES:**
- If the user gets angry, acknowledge it briefly and move to a solution.
- Do not hallucinate legal threats.
- ONE question per turn.
- Do not summarize the total sum. State the monthly payment only.
"""

    def __init__(self, llm_client: LLMClient, system_prompt: str = None):
        self.llm = llm_client
        self.history: List[Dict[str, str]] = []
        
        # Store the base template (unformatted)
        self.base_template = system_prompt if system_prompt and len(system_prompt.strip()) > 0 else self.DEFAULT_RACHEL_CORE
        
        # Construct the full prompt structure (Safety + Constraints + User Prompt)
        self.system_prompt_template = self._build_system_prompt(self.base_template)

    def _build_system_prompt(self, core_content: str) -> str:
        """
        Wraps the user's core prompt with Safety and Anti-Hallucination rules.
        Smartly detects if the prompt is already optimized (has tags) to avoid double-wrapping.
        """
        # If the prompt contains XML tags, it's likely coming from the Optimizer.
        # We trust the Optimizer's structure but prepend Safety Rules.
        if "<user_instructions>" in core_content or "<strict_constraints>" in core_content:
            return f"{self.SAFETY_RULES}\n\n{core_content}"
        
        # If it's a raw user input, we apply the full "Lobotomy" wrapper.
        return f"{self.SAFETY_RULES}\n{self.ANTI_HALLUCINATION_RULES}\n\n<user_instructions>\n{core_content}\n</user_instructions>"

    def update_prompt(self, new_prompt: str):
        """Called by the Simulation Loop when the Optimizer returns a new script."""
        self.base_template = new_prompt
        self.system_prompt_template = self._build_system_prompt(new_prompt)

    def reset(self, defaulter_name: str = "John Doe"):
        """
        Resets conversation history and injects the dynamic persona name.
        This is called at the start of EVERY simulation run.
        """
        # Inject variable if it exists in the template
        final_prompt = self.system_prompt_template.replace("{defaulter_name}", defaulter_name)
        
        # Reset history
        self.history = [{"role": "system", "content": final_prompt}]

    def respond(self, user_input: str = None):
        """Generates a response from the Agent."""
        if user_input:
            self.history.append({"role": "user", "content": user_input})
        
        # Stop sequences prevent the 70B model from writing the user's lines
        stops = ["Defaulter:", "User:", "\n\n", "[Your turn"]
        
        response = self.llm.complete_chat(self.history, stop=stops)
        
        if response:
            self.history.append({"role": "assistant", "content": response})
        
        return response