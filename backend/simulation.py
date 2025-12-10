import time
from agent import DebtCollectionAgent
from personalities import DefaulterAgent
from rich.console import Console

console = Console()

class ConversationSimulator:
    def __init__(self, agent: DebtCollectionAgent, defaulter: DefaulterAgent, max_turns: int = 10):
        self.agent = agent
        self.defaulter = defaulter
        self.max_turns = max_turns
        self.logs = []

    def run(self):
        console.print(f"[bold green]Starting Simulation[/bold green]")
        console.print(f"Defaulter Persona: {self.defaulter.persona.name} ({self.defaulter.persona.personality_traits})")
        
        if not self.agent:
             console.print("[bold red]SYSTEM ERROR: Agent is None[/bold red]")
             return []

        # Initial greeting from Agent
        try:
             agent_msg = self.agent.respond() # Start conversation
        except Exception as e:
             console.print(f"[bold red]SYSTEM ERROR in agent.respond(): {e}[/bold red]")
             agent_msg = None

        if not agent_msg:
            console.print("[bold red]Agent failed to generate greeting (Empty response).[/bold red]")
            return self.logs
        
        self.logs.append({"role": "agent", "content": agent_msg})
        console.print(f"[blue]Agent:[/blue] {agent_msg}")

        for i in range(self.max_turns):
            # Defaulter responds
            defaulter_msg = self.defaulter.respond(agent_msg)
            if not defaulter_msg:
                console.print("[bold red]Defaulter failed to respond.[/bold red]")
                break
            
            self.logs.append({"role": "defaulter", "content": defaulter_msg})
            console.print(f"[red]Defaulter ({self.defaulter.persona.name}):[/red] {defaulter_msg}")

            # Agent responds back
            agent_msg = self.agent.respond(defaulter_msg)
            if not agent_msg:
                console.print("[bold red]Agent failed to respond.[/bold red]")
                break
            
            self.logs.append({"role": "agent", "content": agent_msg})
            console.print(f"[blue]Agent:[/blue] {agent_msg}")

            if "goodbye" in agent_msg.lower() or "bye" in  defaulter_msg.lower():
                break
            

        
        return self.logs
