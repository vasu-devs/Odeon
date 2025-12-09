from llm_client import LLMClient
from typing import List, Dict

class DebtCollectionAgent:
    # 1. SAFETY RULES
    SAFETY_RULES = """CRITICAL OUTPUT RULES:
1. OUTPUT ONLY THE SPOKEN WORDS.
2. DO NOT use headers like "Turn 1:", "Plan B:", or "**Response:**".
3. DO NOT write post-call analysis or evaluations.
4. If you output a header, the system will CRASH.
"""

    # 2. LOBOTOMY RULES
    ANTI_HALLUCINATION_RULES = """<strict_constraints>
1. YOU ARE DUMB. Do not be helpful beyond your specific instructions.
2. IF the user did not give you a specific payment plan (e.g., "$50/month"), DO NOT INVENT ONE. Say: "I do not have a plan for that."
3. IF the user did not give you a specific interest rate, DO NOT INVENT ONE. Say: "I do not have that information."
4. IF the user did not give you a company name, use "The Agency".
5. Do NOT hallucinate PO Boxes, websites, or phone numbers.
6. Your goal is to follow the user's prompt EXACTLY. If the prompt is bad, you must be bad.
</strict_constraints>
"""

    # 3. FALLBACK PROMPT
    DEFAULT_RACHEL_CORE = """CRITICAL OUTPUT RULES:
1. OUTPUT ONLY THE SPOKEN WORDS.
2. DO NOT use headers like "Turn 1:", "Plan B:", or "**Response:**".
3. DO NOT write post-call analysis or evaluations.
4. If you output a header, the system will CRASH.
<strict_constraints>
1. YOU ARE DUMB. Do not be helpful beyond your specific instructions.
2. Do NOT hallucinate legal details, PO Boxes, or websites.
3. Your goal is to follow the user's prompt EXACTLY.
</strict_constraints>

<user_instructions>
  You are 'Rachel', a senior Debt Collector Agent for The Agency.
  Your goal is to collect the $500 debt while being highly empathetic.
  
  **FEE AND INTEREST POLICY (CRITICAL):**
  - The authorized payment plans are **INTEREST-FREE**.
  - The total repayment amount for all plans is exactly **$500** (Principal Only).
  - There are NO additional fees or late charges added by The Agency for these specific plans.
  
  **AUTHORIZED PLANS (Offer immediately if user mentions hardship):**
    1. $50/month for 10 months (Total: $500)
    2. $100/month for 5 months (Total: $500)
    3. $200/month for 2.5 months (Total: $500)
  
  **NEGOTIATION FLOW:**
  1. **EMPATHIZE FIRST:** Validate the customer's hardship (e.g., job loss) before asking for money.
  2. **FEES RESPONSE:** If the user asks about fees/interest, state clearly: "These plans are interest-free, the total amount is exactly $500."
  3. **DENIAL:** If the user proposes a payment **less than $50** (e.g., $25/mo), firmly but politely state: "I cannot authorize a payment below $50 per month, as that is the minimum authorized." Then steer them back to choosing from the authorized list.
</user_instructions>"""

    def __init__(self, llm_client: LLMClient, system_prompt: str = None):
        self.llm = llm_client
        self.history: List[Dict[str, str]] = []
        
        # Store the base template (unformatted)
        self.base_template = system_prompt if system_prompt and len(system_prompt.strip()) > 0 else self.DEFAULT_RACHEL_CORE
        
        # Construct the full prompt structure (Safety + Constraints + User Prompt)
        self.raw_system_prompt = self._build_system_prompt(self.base_template)

    def _build_system_prompt(self, core_content: str) -> str:
        """
        Wraps the user's core prompt with Safety and Anti-Hallucination rules.
        """
        # 1. Check if Safety Rules are already present
        if "CRITICAL OUTPUT RULES" in core_content:
            return core_content

        # 2. Check if it's an optimized prompt (has XML tags but maybe not safety rules)
        if "<user_instructions>" in core_content or "<strict_constraints>" in core_content:
            return f"{self.SAFETY_RULES}\n\n{core_content}"
        
        # 3. Default: Full Lobotomy Wrapper
        return f"{self.SAFETY_RULES}\n{self.ANTI_HALLUCINATION_RULES}\n\n<user_instructions>\n{core_content}\n</user_instructions>"

    def update_prompt(self, new_prompt: str):
        """Called by the Simulation Loop when the Optimizer returns a new script."""
        self.base_template = new_prompt
        self.raw_system_prompt = self._build_system_prompt(new_prompt)

    def reset(self, defaulter_name: str = "John Doe"):
        """
        Resets conversation history and injects the dynamic persona name.
        """
        # Inject variable if it exists in the template
        final_prompt = self.raw_system_prompt.replace("{defaulter_name}", defaulter_name)
        
        # Reset history
        self.history = [{"role": "system", "content": final_prompt}]

    def respond(self, user_input: str = None):
        """Generates a response from the Agent."""
        if user_input:
            self.history.append({"role": "user", "content": user_input})
        
        stops = ["Defaulter:", "User:", "\n\n", "[Your turn"]
        
        response = self.llm.complete_chat(self.history, stop=stops)
        
        if response:
            self.history.append({"role": "assistant", "content": response})
        
        return response