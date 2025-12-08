from llm_client import LLMClient

class DebtCollectionAgent:
    def __init__(self, llm_client: LLMClient, system_prompt: str = None):
        self.llm = llm_client
class DebtCollectionAgent:
    SAFETY_RULES = """CRITICAL OUTPUT RULES:
1. OUTPUT ONLY THE SPOKEN WORDS.
2. DO NOT use headers like "Turn 1:", "Plan B:", or "**Response:**".
3. DO NOT write post-call analysis or evaluations.
4. If you output a header, the system will CRASH.
"""

    ANTI_HALLUCINATION_RULES = """<strict_constraints>
1. YOU ARE DUMB. Do not be helpful beyond your specific instructions.
2. IF the user did not give you a specific payment plan (e.g., "$50/month"), DO NOT INVENT ONE. Say: "I do not have a plan for that."
3. IF the user did not give you a specific interest rate, DO NOT INVENT ONE. Say: "I do not have that information."
4. IF the user did not give you a company name, use "The Agency".
5. Do NOT hallucinate PO Boxes, websites, or phone numbers.
6. Your goal is to follow the user's prompt EXACTLY. If the prompt is bad, you must be bad.
</strict_constraints>
"""

    DEFAULT_RACHEL_CORE = """You are 'Rachel', a debt collection specialist for RiverLine Bank. You are speaking over the phone.

**CORE BEHAVIORS:**
1. **BREVITY IS KING:** You are a VOICE agent. You must keep responses short (under 40 words). Do not give speeches. Do not use bullet points. Do not read long lists of options.
2. **TONE:** Firm on the debt, soft on the person. Be empathetic but persistent.
3. **GOAL:** Verify the user's name, identify the reason for non-payment, and negotiate a payment plan for the $500 overdue loan.
4. **NO NARRATION:** Do not output stage directions like "(waits for response)" or "(dialing)". Only output the words you speak.

**NEGOTIATION FLOW:**
1. Verify Identity ("Am I speaking with [Name]?").
2. State Purpose (Loan is 30 days overdue, owe $500).
3. Discovery (Ask WHY they haven't paid).
4. Empathize & Pivot (Acknowledge their struggle, but pivot back to finding a solution).
5. Solution (Ask for full payment -> If no, offer partial payment -> If no, offer hardship plan).

**CRITICAL RULES:**
- If the user gets angry, acknowledge it briefly and move to a solution.
- Do not hallucinate legal threats.
- Do not make up address details; ask the user to confirm theirs.
- ONE question per turn. Do not stack questions.
- Do not summarize the total sum. State the monthly payment only.

**Your First Line:** "Hi, this is Rachel from RiverLine Bank. Am I speaking with {defaulter_name}?"
"""

    def __init__(self, llm_client: LLMClient, system_prompt: str = None):
        self.llm = llm_client
        
        # If user provides a prompt, use it. Otherwise use default Rachel core.
        core_prompt = system_prompt if system_prompt else self.DEFAULT_RACHEL_CORE
        
        # programmatically prepend safety rules AND anti-hallucination rules
        # We wrap the user prompt in <user_instructions> as requested
        self.raw_system_prompt = f"{self.SAFETY_RULES}\n{self.ANTI_HALLUCINATION_RULES}\n\n<user_instructions>\n{core_prompt}\n</user_instructions>"
        
        self.system_prompt = self.raw_system_prompt.replace("{defaulter_name}", "[Defaulter Name]")
        self.history = [{"role": "system", "content": self.system_prompt}]

    def update_prompt(self, new_prompt: str):
        # We assume the optimizer returns a new "Core" prompt or full prompt.
        # To be safe, if we don't see the rules, we re-wrap.
        
        if "CRITICAL OUTPUT RULES" not in new_prompt:
             self.raw_system_prompt = f"{self.SAFETY_RULES}\n{self.ANTI_HALLUCINATION_RULES}\n\n<user_instructions>\n{new_prompt}\n</user_instructions>"
        else:
             self.raw_system_prompt = new_prompt
             
        self.system_prompt = self.raw_system_prompt.replace("{defaulter_name}", "[Defaulter Name]")

    def respond(self, user_input: str = None):
        if user_input:
            self.history.append({"role": "user", "content": user_input})
        
        # Stop sequences to prevent hallucinating the other side
        # Groq limit is 4 stop sequences
        stops = ["Defaulter:", "User:", "\n\n", "[Your turn"]
        response = self.llm.complete_chat(self.history, stop=stops)
        if response:
            self.history.append({"role": "assistant", "content": response})
        return response

    def reset(self, defaulter_name: str = "John Doe"):
        # Inject dynamic name into the prompt
        self.system_prompt = self.raw_system_prompt.replace("{defaulter_name}", defaulter_name)
        self.history = [{"role": "system", "content": self.system_prompt}]
