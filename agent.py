from llm_client import LLMClient

class DebtCollectionAgent:
    def __init__(self, llm_client: LLMClient, system_prompt: str = None):
        self.llm = llm_client
        self.default_system_prompt = """You are a professional, polite, but firm debt collection agent for the 'RiverLine Bank'.
Your goal is to collect a debt of $500 for a personal loan, 30 days overdue.
Verify the user's name first.
Then ask for the reason for non-payment.
Negotiate a payment plan if they cannot pay in full.
Be empathetic but stay focused on the collection.
Keep your responses concise, suitable for a voice interface (speech-to-text).
"""
        self.system_prompt = system_prompt if system_prompt else self.default_system_prompt
        self.history = [{"role": "system", "content": self.system_prompt}]

    def update_prompt(self, new_prompt: str):
        self.system_prompt = new_prompt
        # Reset history with new prompt
        self.history = [{"role": "system", "content": self.system_prompt}]

    def respond(self, user_input: str = None):
        if user_input:
            self.history.append({"role": "user", "content": user_input})
        
        response = self.llm.complete_chat(self.history)
        if response:
            self.history.append({"role": "assistant", "content": response})
        return response

    def reset(self):
        self.history = [{"role": "system", "content": self.system_prompt}]
