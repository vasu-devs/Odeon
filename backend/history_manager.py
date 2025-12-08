import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any

class HistoryManager:
    def __init__(self, db_file="history.db"):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                success_rate REAL,
                total_cycles INTEGER,
                config TEXT,
                results TEXT,
                optimization_history TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def load_history(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_file)
        # Use a dict factory to get dictionary results directly if preferred, 
        # but manual mapping gives us control over JSON decoding.
        c = conn.cursor()
        c.execute('SELECT id, timestamp, success_rate, total_cycles, config, results, optimization_history FROM runs ORDER BY timestamp DESC')
        rows = c.fetchall()
        conn.close()

        history = []
        for row in rows:
            try:
                history.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "success_rate": row[2],
                    "total_cycles": row[3],
                    "config": json.loads(row[4]),
                    "results": json.loads(row[5]),
                    "optimization_history": json.loads(row[6])
                })
            except json.JSONDecodeError:
                continue # Skip corrupted rows
                
        return history

    def save_run(self, run_data: Dict[str, Any]):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Ensure ID and Timestamp
        run_id = run_data.get("id") or datetime.now().strftime("%Y%m%d%H%M%S")
        timestamp = run_data.get("timestamp") or datetime.now().isoformat()
        
        c.execute('''
            INSERT OR REPLACE INTO runs (id, timestamp, success_rate, total_cycles, config, results, optimization_history)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            timestamp,
            run_data.get("success_rate", 0.0),
            run_data.get("total_cycles", 0),
            json.dumps(run_data.get("config", {})),
            json.dumps(run_data.get("results", [])),
            json.dumps(run_data.get("optimization_history", []))
        ))
        
        conn.commit()
        conn.close()

    def delete_run(self, run_id: str):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('DELETE FROM runs WHERE id = ?', (run_id,))
        conn.commit()
        conn.close()

    def clear_history(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('DELETE FROM runs')
        conn.commit()
        conn.close()
