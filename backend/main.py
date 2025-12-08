import argparse
import os
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()

from llm_client import LLMClient
from agent import DebtCollectionAgent
from personalities import DefaulterGenerator, DefaulterAgent
from simulation import ConversationSimulator
from evaluator import Evaluator
from optimizer import ScriptOptimizer

console = Console()

from rich.prompt import Prompt, Confirm

def setup_wizard():
    console.clear()
    console.rule("[bold cyan]Voice Agent Gym - Setup Wizard[/bold cyan]")
    
    # 1. Select Provider
    providers = ["gemini", "groq", "openai", "local"]
    provider = Prompt.ask("Select LLM Provider", choices=providers, default="groq")
    
    # Defaults
    api_key = None
    model_name = None
    base_url = None
    
    # Dictionary to hold clients for different roles (Agent, Persona, Evaluator)
    # Default: All same
    clients = {}

    # 2. Configure Provider
    if provider == "groq":
        console.print("[green]Groq selected! Applying recommended optimized models...[/green]")
        default_key = os.getenv("GROQ_API_KEY", "")
        api_key = Prompt.ask("Enter Groq API Key", default=default_key, password=True)
        
        # Instantiate 3 clients with recommended models
        clients["agent"] = LLMClient(provider="groq", api_key=api_key, model_name="llama-3.1-8b-instant")
        clients["generator"] = LLMClient(provider="groq", api_key=api_key, model_name="llama-3.1-8b-instant")
        clients["evaluator"] = LLMClient(provider="groq", api_key=api_key, model_name="llama-3.1-8b-instant") 
        clients["optimizer"] = LLMClient(provider="groq", api_key=api_key, model_name="llama-3.1-8b-instant")
        
        console.print("[dim]Persona: llama-3.1-8b-instant[/dim]")
        console.print("[dim]Agent (SUT): llama-3.1-8b-instant[/dim]")
        console.print("[dim]Evaluator: llama-3.1-8b-instant[/dim]")
        
        return clients

    elif provider == "gemini":
        default_key = os.getenv("GEMINI_API_KEY", "")
        api_key = Prompt.ask("Enter Gemini API Key", default=default_key, password=True)
        model_name = Prompt.ask("Enter Model Name", default="gemini-flash-latest")
    
    elif provider == "openai":
        default_key = os.getenv("OPENAI_API_KEY", "")
        api_key = Prompt.ask("Enter OpenAI API Key", default=default_key, password=True)
        model_name = Prompt.ask("Enter Model Name", default="gpt-4o")

    elif provider == "local":
        base_url = Prompt.ask("Enter Base URL", default="http://localhost:1234/v1")
        model_name = Prompt.ask("Enter Model Name (optional)", default="local-model")
        api_key = "lm-studio"

    # For non-Groq (or standard), use same client for all
    client = LLMClient(provider=provider, api_key=api_key, model_name=model_name, base_url=base_url)
    return {
        "agent": client,
        "generator": client,
        "evaluator": client,
        "optimizer": client
    }

def run_simulation_loop(max_cycles: int, batch_size: int = 5, pass_threshold: float = 0.8):
    # Interactive Setup
    clients = setup_wizard()
    
    agent = DebtCollectionAgent(clients["agent"])
    generator = DefaulterGenerator(clients["generator"])
    evaluator = Evaluator(clients["evaluator"])
    optimizer = ScriptOptimizer(clients["optimizer"])

    for cycle in range(1, max_cycles + 1):
        console.rule(f"[bold yellow]Optimization Cycle {cycle}/{max_cycles}[/bold yellow]")
        
        batch_results = []
        failures = []
        
        # --- Batch Execution ---
        for b in range(1, batch_size + 1):
            console.print(f"\n[dim]--- Simulation {b}/{batch_size} ---[/dim]")
            
            # 1. Generate Persona
            persona = generator.generate_persona()
            defaulter = DefaulterAgent(persona, clients["generator"])
            
            # Inject name into Agent (SUT)
            agent.reset(defaulter_name=persona.name)
            
            console.print(f"Testing against: [bold cyan]{persona.name}[/bold cyan] - {persona.objection_type}")
    
            # 2. Run Simulation
            simulator = ConversationSimulator(agent, defaulter)
            logs = simulator.run()
    
            # 3. Evaluate
            result = evaluator.evaluate_conversation(logs)
            
            # Display Score
            table = Table(title=f"Result: {persona.name}")
            table.add_column("Metric", style="cyan")
            table.add_column("Score", style="magenta")
            
            table.add_row("Repetition", str(result.metrics.repetition))
            table.add_row("Negotiation", str(result.metrics.negotiation))
            table.add_row("Empathy", str(result.metrics.empathy))
            table.add_row("Overall", str(result.overall_rating))
            
            console.print(table)
            console.print(f"[bold]Feedback:[/bold] {result.feedback}")
            
            batch_results.append(result)
            
            if result.overall_rating < 8.5:
                failures.append({
                    "persona": persona,
                    "result": result,
                    "logs": logs
                })
        
        # --- Batch Analysis ---
        passes = len([r for r in batch_results if r.overall_rating >= 8.5])
        success_rate = passes / batch_size
        
        console.rule("[bold green]Batch Report[/bold green]")
        console.print(f"Cycle {cycle} Result: [bold]{passes}/{batch_size} Passed[/bold] ({success_rate*100:.1f}%)")
        
        if success_rate >= pass_threshold:
            console.print(f"[bold green]SUCCESS! Threshold ({pass_threshold*100}%) met. stopping optimization.[/bold green]")
            console.print(f"Final Agent Prompt saved.")
            break
        
        if cycle < max_cycles:
            if not failures:
                console.print("[yellow]Odd... Success rate low but no failures captured? Continuing...[/yellow]")
                continue
                
            console.print(f"[bold red]Threshold not met. Optimizing based on {len(failures)} failures...[/bold red]")
            
            # 4. Self-Correction
            # Use raw_system_prompt to avoid baking in the current defaulter's name
            new_prompt = optimizer.optimize_screenplay(agent.raw_system_prompt, failures)
            agent.update_prompt(new_prompt)
            console.print("[dim]New prompt applied for next round.[/dim]")
            
    console.print("[bold blue]Test Suite Completed.[/bold blue]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Agent Auto-Tester & Optimizer")
    parser.add_argument("--cycles", type=int, default=5, help="Max optimization cycles")
    parser.add_argument("--batch", type=int, default=5, help="Simulations per cycle")
    parser.add_argument("--threshold", type=float, default=0.8, help="Pass threshold (0.0-1.0)")
    args = parser.parse_args()
    
    run_simulation_loop(args.cycles, args.batch, args.threshold)
