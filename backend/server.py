import asyncio
import json
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import traceback

# Import existing logic
from llm_client import LLMClient
from agent import DebtCollectionAgent
from personalities import DefaulterGenerator, DefaulterAgent
from simulation import ConversationSimulator
from evaluator import Evaluator
from optimizer import ScriptOptimizer
import simulation  # To override console
import main  # To override console if needed
from history_manager import HistoryManager

# Setup Request Object
class ThresholdConfig(BaseModel):
    repetition: float
    negotiation: float
    empathy: float
    overall: float

class SimulationConfig(BaseModel):
    api_key: str
    model_name: str
    base_prompt: str
    max_cycles: int
    batch_size: int
    thresholds: ThresholdConfig

app = FastAPI()
history_manager = HistoryManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Logger classes) ...
class WebSocketLogger:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    def print(self, *args, **kwargs):
        pass

log_queue = asyncio.Queue()

class AsyncConsoleLogger:
    def print(self, *args, **kwargs):
        msg = " ".join(str(arg) for arg in args)
        log_queue.put_nowait(msg)
    
    def rule(self, *args, **kwargs):
        self.print("---", *args, "---")

    def clear(self):
        pass

@app.get("/history")
async def get_history():
    return history_manager.load_history()

@app.delete("/history/{run_id}")
async def delete_history(run_id: str):
    history_manager.delete_run(run_id)
    return {"status": "success"}

@app.websocket("/ws/simulate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    original_console = simulation.console
    simulation.console = AsyncConsoleLogger()
    main.console = simulation.console 
    
    run_id = datetime.now().strftime("%Y%m%d%H%M%S")
    all_results_storage = []
    optimization_storage = []
    config = None
    final_success_rate = 0.0
    cycle = 0

    try:
        data = await websocket.receive_text()
        config_dict = json.loads(data)
        config = SimulationConfig(**config_dict)
        
        # Initialize Clients
        agent_client = LLMClient(provider="groq", api_key=config.api_key, model_name=config.model_name)
        
        clients = {
            "agent": agent_client,
            "generator": agent_client, 
            "evaluator": agent_client,
            "optimizer": agent_client
        }
        
        # Initialize Components
        agent = DebtCollectionAgent(clients["agent"], system_prompt=config.base_prompt)
        generator = DefaulterGenerator(clients["generator"])
        evaluator = Evaluator(clients["evaluator"])
        optimizer = ScriptOptimizer(clients["optimizer"])
        
        # Start Log Streamer Task
        async def stream_logs():
            while True:
                msg = await log_queue.get()
                await websocket.send_json({"type": "log", "message": msg})
                log_queue.task_done()
        
        log_task = asyncio.create_task(stream_logs())

        await websocket.send_json({"type": "log", "message": "Starting Simulation Loop..."})

        # Run Loop Configuration
        batch_size = config.batch_size
        max_cycles = config.max_cycles
        
        target_repetition = config.thresholds.repetition
        target_negotiation = config.thresholds.negotiation
        target_empathy = config.thresholds.empathy
        target_overall = config.thresholds.overall

        # Start with the initial prompt (wrapped by Agent)
        current_prompt = agent.raw_system_prompt

        for cycle in range(1, max_cycles + 1):
            await websocket.send_json({"type": "log", "message": f"--- Cycle {cycle}/{max_cycles} ---"})
            
            batch_results = []
            batch_passes = 0
            
            for b in range(1, batch_size + 1):
                await websocket.send_json({"type": "log", "message": f"Simulating {b}/{batch_size}..."})
                
                # 1. Generate Persona (Sync task running in thread)
                persona = await asyncio.to_thread(generator.generate_persona)
                defaulter = DefaulterAgent(persona, clients["generator"])
                
                # Reset agent with key details
                agent.reset(defaulter_name=persona.name)
                current_prompt = agent.raw_system_prompt
                
                # 2. Run Simulation (Sync task running in thread)
                sim = ConversationSimulator(agent, defaulter)
                logs = await asyncio.to_thread(sim.run)
                
                # 3. Evaluate (Async task - direct await)
                result = await evaluator.evaluate(logs)
                
                # GRANULAR PASS CHECK
                passed = (
                    result.metrics.repetition >= target_repetition and
                    result.metrics.negotiation >= target_negotiation and
                    result.metrics.empathy >= target_empathy and
                    result.overall_rating >= target_overall
                )

                if passed:
                    batch_passes += 1
                
                new_prompt_str = None
                
                # Calculate current cumulative rate
                current_rate = batch_passes / b
                
                # 4. Immediate Optimization if Failed
                if not passed:
                    # Construct detailed failure reason
                    reasons = []
                    if result.metrics.repetition < target_repetition:
                        reasons.append(f"Repetition {result.metrics.repetition}<{target_repetition}")
                    if result.metrics.negotiation < target_negotiation:
                        reasons.append(f"Negotiation {result.metrics.negotiation}<{target_negotiation}")
                    if result.metrics.empathy < target_empathy:
                        reasons.append(f"Empathy {result.metrics.empathy}<{target_empathy}")
                    if result.overall_rating < target_overall:
                        reasons.append(f"Overall {result.overall_rating}<{target_overall}")
                    
                    failure_msg = ", ".join(reasons)
                    await websocket.send_json({"type": "log", "message": f"Scenario Failed: {failure_msg}. Rate: {current_rate:.1%}. Optimizing..."})
                    
                    # We optimize based on this single failure for immediate feedback
                    single_failure = [{
                        "persona": persona,
                        "result": result,
                        "logs": logs
                    }]
                    
                    try:
                        # CRITICAL FIX: optimize_screenplay is async, do NOT use to_thread
                        # Pass specific targets to optimizer
                        new_prompt = await optimizer.optimize_screenplay(
                            current_prompt, 
                            single_failure, 
                            previous_success_rate=current_rate, 
                            target_thresholds=config.thresholds
                        )
                        
                        agent.update_prompt(new_prompt)
                        new_prompt_str = new_prompt
                        
                        opt_entry = {
                            "cycle": cycle,
                            "old_prompt": current_prompt,
                            "new_prompt": new_prompt,
                            "reasoning": f"Optimized after scenario {b} failure ({failure_msg})."
                        }
                        optimization_storage.append(opt_entry)
                        
                        await websocket.send_json({
                            "type": "optimization",
                            **opt_entry
                        })
                        await websocket.send_json({"type": "log", "message": "Prompt Updated."})
                        
                    except Exception as opt_err:
                        # Print full traceback to console for debugging
                        traceback.print_exc()
                        await websocket.send_json({"type": "log", "message": f"[red]Optimization Error: {opt_err}[/red]"})
                
                else:
                     await websocket.send_json({"type": "log", "message": f"Scenario Passed. Rate {current_rate:.1%}."})

                # Add to storage
                result_dict = {
                    "cycle": cycle,
                    "persona": persona.dict(),
                    "score": result.overall_rating,
                    "metrics": result.metrics.dict(),
                    "transcript": logs,
                    "feedback": result.feedback,
                    "passed": passed,
                    "prompt_used": current_prompt,
                    "updated_prompt": new_prompt_str
                }
                all_results_storage.append(result_dict)

                # Send Frontend Event
                transcript_text = "\n".join([f"{l['role']}: {l['content']}" for l in logs])
                
                await websocket.send_json({
                    "type": "result",
                    "cycle": cycle,
                    "persona": persona.name,
                    "score": result.overall_rating,
                    "metrics": result.metrics.dict(),
                    "transcript": transcript_text,
                    "feedback": result.feedback,
                    "passed": passed,
                    "prompt_used": current_prompt,
                    "updated_prompt": new_prompt_str
                })

                batch_results.append(result)
                await asyncio.sleep(0.1)

            final_success_rate = batch_passes / batch_size
            
            # Calculate Batch Averages
            if batch_results:
                avg_rep = sum(r.metrics.repetition for r in batch_results) / batch_size
                avg_neg = sum(r.metrics.negotiation for r in batch_results) / batch_size
                avg_emp = sum(r.metrics.empathy for r in batch_results) / batch_size
                avg_overall = sum(r.overall_rating for r in batch_results) / batch_size
                
                await websocket.send_json({"type": "log", "message": f"Cycle {cycle} Stats: Rep={avg_rep:.1f}, Neg={avg_neg:.1f}, Emp={avg_emp:.1f}, Overall={avg_overall:.1f}"})

                # STRICT SUCCESS CONDITION
                if (avg_rep >= target_repetition and
                    avg_neg >= target_negotiation and
                    avg_emp >= target_empathy and
                    avg_overall >= target_overall):
                    
                    await websocket.send_json({"type": "log", "message": f"[bold green]SUCCESS! All targets met in Cycle {cycle}. Stopping Optimization.[/bold green]"})
                    # success_rate = final_success_rate # For history
                    break
            else:
                await websocket.send_json({"type": "log", "message": "Cycle complete (no results to average)."})

        await websocket.send_json({"type": "log", "message": "Optimization Complete."})
        log_task.cancel()
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        traceback.print_exc()
    finally:
        # ALWAYS SAVE HISTORY (Even if empty, to show the attempt)
        if config:
            try:
                await websocket.send_json({"type": "log", "message": f"Saving Simulation History (Run ID: {run_id})..."})
            except Exception:
                pass # Socket likely closed

            # Recalculate success rate based on actual results stored
            if all_results_storage:
                passed_count = sum(1 for r in all_results_storage if r.get('passed', False))
                final_success_rate = passed_count / len(all_results_storage)
            else:
                final_success_rate = 0.0

            run_data = {
                "id": run_id,
                "timestamp": datetime.now().isoformat(),
                "config": config.dict(),
                "results": all_results_storage,
                "optimization_history": optimization_storage,
                "success_rate": final_success_rate,
                "total_cycles": cycle
            }
            try:
                await asyncio.to_thread(history_manager.save_run, run_data)
                try:
                    await websocket.send_json({"type": "log", "message": "History Saved."})
                except Exception:
                    pass
            except Exception as hist_e:
                print(f"History Save Failed: {hist_e}")
        
        simulation.console = original_console

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)