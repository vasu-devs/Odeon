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
        
        # programmatically prepend safety rules
        self.raw_system_prompt = f"{self.SAFETY_RULES}\n\n{core_prompt}"
        
        self.system_prompt = self.raw_system_prompt.replace("{defaulter_name}", "[Defaulter Name]")
        self.history = [{"role": "system", "content": self.system_prompt}]

    def update_prompt(self, new_prompt: str):
        # We assume new_prompt coming from optimizer might NOT have rules if the optimizer rewrote just the core?
        # OR the optimizer returns the full prompt? 
        # The optimizer usually rewrites the whole thing.
        # User instruction: "The Backend wraps it in safety rules... The Optimizer evolves it... The final output is an optimized version".
        # If the optimizer sees the full prompt (including rules) and optimizes it, it might keep the rules. 
        # BUT if I force prepend, I might duplicate.
        # Let's check `optimizer.py`. It takes `current_prompt` (which now has rules).
        # It says "Rewrite the System Prompt...".
        # If I wrap it here again, I need to be careful.
        # However, for the INITIAL User Input (from UI), it definitely needs wrapping.
        # If `update_prompt` is called by `server.py` with `new_prompt` from Optimizer, 
        # check if it already has rules?
        # User said: "Logic: final = SAFETY + user_prompt".
        # I'll stick to wrapping user input. For optimizer updates, I'll trust the optimizer 
        # OR I should wrap if it seems missing.
        # Safest bet: The optimizer returns a "System Prompt". 
        # If I want to enforce rules, I should probably strip old rules and re-add, or just treat the input as the core.
        # Let's assume `update_prompt` is called with a FULL prompt from optimizer, so I won't re-wrap it to avoid duplication,
        # UNLESS the user explicitly wants me to wrap strictly user inputs.
        # Actually, `server.py` calls `update_prompt` with the optimizer output.
        # The optimizer output is based on `current_prompt`.
        # I will modify `update_prompt` to just set it, assuming optimizer handles it, 
        # BUT for the initial set up from UI, `__init__` handles the wrapping.
        
        # Wait, if `server.py` takes `config.base_prompt` and calls `agent.update_prompt(config.base_prompt)`,
        # then `update_prompt` MUST wrap it if it's a raw user string.
        # But if it's from optimizer...
        # I will make `update_prompt` wrap it ONLY IF it acts as a "reset" from config. 
        # But `server.py` logic uses `update_prompt` for both.
        # I will rename the method or add a flag. 
        # Let's use `set_system_prompt` for raw user input (wrapped) and `set_full_prompt` for optimizer.
        # Or just checking if "CRITICAL OUTPUT RULES" is inside.
        
        if "CRITICAL OUTPUT RULES" not in new_prompt:
             self.raw_system_prompt = f"{self.SAFETY_RULES}\n\n{new_prompt}"
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
