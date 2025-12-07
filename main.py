import argparse
import os
from rich.console import Console
from rich.table import Table

from llm_client import LLMClient
from agent import DebtCollectionAgent
from personalities import DefaulterGenerator, DefaulterAgent
from simulation import ConversationSimulator
from evaluator import Evaluator
from optimizer import ScriptOptimizer

console = Console()

def run_simulation_loop(iterations: int):
    llm = LLMClient()
    agent = DebtCollectionAgent(llm)
    generator = DefaulterGenerator(llm)
    evaluator = Evaluator(llm)
    optimizer = ScriptOptimizer(llm)

    evaluation_history = []

    for i in range(1, iterations + 1):
        console.rule(f"[bold yellow]Iteration {i}/{iterations}[/bold yellow]")
        
        # 1. Generate Persona
        persona = generator.generate_persona()
        defaulter = DefaulterAgent(persona, llm)
        console.print(f"Testing against: [bold cyan]{persona.name}[/bold cyan] - {persona.objection_type}")

        # 2. Run Simulation
        simulator = ConversationSimulator(agent, defaulter)
        logs = simulator.run()

        # 3. Evaluate
        result = evaluator.evaluate_conversation(logs)
        evaluation_history.append(result)
        
        # Display Score
        table = Table(title="Evaluation Result")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", style="magenta")
        table.add_row("Repetition", str(result.repetition_score))
        table.add_row("Negotiation", str(result.negotiation_score))
        table.add_row("Empathy", str(result.empathy_score))
        table.add_row("Overall", str(result.overall_rating))
        console.print(table)
        console.print(f"[bold]Feedback:[/bold] {result.feedback}")

        # 4. Self-Correction (if not the last iteration)
        if i < iterations:
            console.print("[bold green]Optimizing Agent Script...[/bold green]")
            new_prompt = optimizer.optimize_screenplay(agent.system_prompt, evaluation_history)
            agent.update_prompt(new_prompt)
            console.print("[dim]New prompt applied for next round.[/dim]")
            console.print(f"[dim]Prompt preview: {new_prompt[:100]}...[/dim]")

    console.rule("[bold green]Final Report[/bold green]")
    avg_score = sum([r.overall_rating for r in evaluation_history]) / len(evaluation_history)
    console.print(f"Average Overall Score: {avg_score:.2f}/10")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice Agent Auto-Tester & Optimizer")
    parser.add_argument("--iterations", type=int, default=3, help="Number of self-correction loops")
    args = parser.parse_args()
    
    if not os.getenv("GEMINI_API_KEY"):
        console.print("[bold red]Please set GEMINI_API_KEY environment variable[/bold red]")
    else:
        run_simulation_loop(args.iterations)
