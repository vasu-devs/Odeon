import asyncio
import json
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing logic
from llm_client import LLMClient
from agent import DebtCollectionAgent
from personalities import DefaulterGenerator, DefaulterAgent
from simulation import ConversationSimulator
from evaluator import Evaluator
from optimizer import ScriptOptimizer
# ... previous imports
import simulation  # To override console
import main  # To override console if needed
from history_manager import HistoryManager
from datetime import datetime

# Setup Request Object
class SimulationConfig(BaseModel):
    api_key: str
    model_name: str
    base_prompt: str
    max_cycles: int
    batch_size: int
    threshold: float

app = FastAPI()
history_manager = HistoryManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (Logger classes remain the same) ...
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
        
        agent = DebtCollectionAgent(clients["agent"])
        # Explicitly set the prompt provided by user (no fallback if empty string provided, intended behavior)
        if config.base_prompt:
             agent.update_prompt(config.base_prompt)
        
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

        # Run Loop
        batch_size = config.batch_size
        max_cycles = config.max_cycles
        pass_threshold = config.threshold
        min_score = pass_threshold * 10

        passed_final = False
        all_results_storage = []
        optimization_storage = []

        # Tracking for history
        run_id = datetime.now().strftime("%Y%m%d%H%M%S")

        for cycle in range(1, max_cycles + 1):
            await websocket.send_json({"type": "log", "message": f"--- Cycle {cycle}/{max_cycles} ---"})
            
            batch_results = []
            failures = []
            
            for b in range(1, batch_size + 1):
                await websocket.send_json({"type": "log", "message": f"Simulating {b}/{batch_size}..."})
                
                # 1. Generate Persona
                persona = await asyncio.to_thread(generator.generate_persona)
                defaulter = DefaulterAgent(persona, clients["generator"])
                
                agent.reset(defaulter_name=persona.name)
                current_prompt = agent.raw_system_prompt
                
                # 2. Run Simulation
                sim = ConversationSimulator(agent, defaulter)
                logs = await asyncio.to_thread(sim.run)
                
                # 3. Evaluate
                result = await asyncio.to_thread(evaluator.evaluate_conversation, logs)
                
                passed = result.overall_rating >= min_score
                new_prompt_str = None
                
                # 4. Immediate Optimization if Failed
                if not passed:
                    await websocket.send_json({"type": "log", "message": f"Scenario Failed ({result.overall_rating}/{min_score}). Optimizing..."})
                    
                    # We optimize based on this single failure for immediate feedback
                    # Note: Passing single failure might be volatile, but requested by user ("modify after each scenario")
                    single_failure = [{
                        "persona": persona,
                        "result": result,
                        "logs": logs
                    }]
                    
                    try:
                        new_prompt = await asyncio.to_thread(
                            optimizer.optimize_screenplay, 
                            current_prompt, 
                            single_failure, 
                            previous_success_rate=0.0, # Immediate fail
                            target_threshold=pass_threshold
                        )
                        
                        agent.update_prompt(new_prompt)
                        new_prompt_str = new_prompt
                        
                        opt_entry = {
                            "cycle": cycle,
                            "old_prompt": current_prompt,
                            "new_prompt": new_prompt,
                            "reasoning": f"Optimized after scenario {b} failure."
                        }
                        optimization_storage.append(opt_entry)
                        
                        await websocket.send_json({
                            "type": "optimization",
                            **opt_entry
                        })
                        await websocket.send_json({"type": "log", "message": "Prompt Updated."})
                        
                    except Exception as opt_err:
                        console.print(f"[red]Optimization Error: {opt_err}[/red]")

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
                    "metrics": result.metrics.dict(), # Send detailed metrics
                    "transcript": transcript_text,
                    "feedback": result.feedback,
                    "passed": passed,
                    "prompt_used": current_prompt,
                    "updated_prompt": new_prompt_str
                })

                batch_results.append(result)
                await asyncio.sleep(0.1)

                # Check if we should stop early?
                # User said "till we get the threshold". If this scenario PASSED, and it's 100% success rate so far?
                # For now, we continue the batch to ensure consistency, 
                # but the prompt keeps getting better (hopefully).

            # Analysis
            passes = len([r for r in batch_results if r.overall_rating >= min_score])
        
        # Save History
        await websocket.send_json({"type": "log", "message": "Saving Simulation History..."})
        run_data = {
            "id": run_id,
            "timestamp": datetime.now().isoformat(),
            "config": config.dict(),
            "results": all_results_storage,
            "optimization_history": optimization_storage,
            "success_rate": success_rate, # Final cycle rate
            "total_cycles": cycle
        }
        await asyncio.to_thread(history_manager.save_run, run_data)

        await websocket.send_json({"type": "log", "message": "Optimization Complete."})
        log_task.cancel()
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
        import traceback
        traceback.print_exc()
    finally:
        simulation.console = original_console

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
