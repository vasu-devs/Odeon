# Odeon - AI Agent Optimization Platform

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-19.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Odeon** is an advanced AI testing and optimization platform designed to simulate, evaluate, and self-correct AI agent behaviors. It automates the critical loop of generating diverse test scenarios, running high-fidelity conversations, scoring performance against strict KPIs, and iteratively rewriting the system prompt to meet specific business targets.

[![Visualize in MapMyRepo](https://mapmyrepo.vasudev.live/badge.svg)](https://mapmyrepo.vasudev.live/?user=vasu-devs&repo=Odeon)

---

## 🚀 Key Features

*   **⚡ Autonomous Optimization Loop**: Automatically generates diverse user personas (e.g., "Angry Debtor", "Confused Elderly"), runs simulations, evaluates performance, and rewrites the agent's prompt if KPIs are missed.
*   **📡 Real-Time Simulation Stream**: Watch agent-user interactions unfold live via deeply integrated WebSockets, providing immediate insight into agent behavior.
*   **🔄 Prompt Evolution Diffing**: Visualizes exactly what changed in the system prompt between iterations using a git-style Red/Green diff viewer.
*   **🎨 Strict Monochrome UI**: A high-end, distraction-free "Neumorphic" interface designed for focus and clarity, built with the latest Tailwind CSS 4.
*   **📊 Comprehensive Metrics**: Tracks **Repetition**, **Negotiation**, and **Empathy** scores with strict numeric thresholds (1-10) to ensure quality.
*   **🗄️ Simulation History**: Archives every run with full transcripts, scores, and evolved prompts in a local SQLite database for regression testing.
*   **🎛️ Interactive Controls**: Fine-tune thresholds, max optimization cycles, and switch models (Llama 3 via Groq) on the fly.

---

## 🏗️ System Architecture

Odeon employs a modern, decoupled architecture to ensure speed and scalability.

```mermaid
graph TD
    User[User / Browser] -->|HTTP / WS| FE[Frontend (React + Vite)]
    FE -->|WebSocket| API[Backend API (FastAPI)]
    
    subgraph "Backend Core"
        API -->|Dispatch| Sim[Simulator Engine]
        Sim -->|Generate| Gen[Persona Generator]
        Sim -->|Chat| Agent[Agent LLM]
        Sim -->|Chat| UserSim[User Simulator LLM]
        Sim -->|Grade| Eval[Evaluator]
        Sim -->|Optimize| Opt[Prompt Optimizer]
        
        Agent <--> Groq[Groq Llama 3 API]
        UserSim <--> Groq
        Eval <--> Groq
        Opt <--> Groq
    end
    
    API -->|Read/Write| DB[(SQLite History DB)]
```

---

## 🛠️ Technology Stack

### Backend
*   **Python 3.10+**: Core logic and scripting.
*   **FastAPI**: High-performance async API framework for REST and WebSockets.
*   **LangChain**: Orchestration of LLM chains and structured output parsing.
*   **Groq API**: Ultra-low latency inference for Llama 3 models, enabling rapid simulation cycles.
*   **Pydantic**: Strict data validation for configuration and API models.
*   **SQLite**: Lightweight, zero-config persistence for run history.

### Frontend
*   **React 19**: Utilizing the latest concurrent features and Hooks.
*   **Vite**: Next-generation frontend tooling for instant dev server start.
*   **TypeScript**: Full type safety across the entire UI codebase.
*   **Tailwind CSS 4**: Utility-first styling with custom Neumorphic utilities and animations.
*   **Recharts**: For visualizing optimization trends (planned).

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

1.  **Python 3.10** or higher.
2.  **Node.js 18** or higher (and `npm`).
3.  **Groq API Key**: Get one for free from [console.groq.com](https://console.groq.com).

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/odeon.git
cd odeon
```

### 2. Backend Setup
Navigate to the `backend` directory and set up the Python environment.

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Configuration (.env)**
Create a `.env` file in the `backend/` directory with your keys:

```env
# Required for Optimization & Simulation
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: Google Gemini Key if used for specific sub-tasks
GEMINI_API_KEY=your_gemini_key
```

### 3. Frontend Setup
Open a new terminal, navigate to the `frontend` directory, and install Node dependencies.

```bash
cd frontend

# Install packages
npm install
```

---

## 🏃‍♂️ Running the Application

You need to run both the backend server and the frontend development server simultaneously.

### Terminal 1: Backend
```bash
cd backend
# Ensure venv is active
python server.py
```
*The server will start on `http://localhost:8000`*

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```
*The UI will launch at `http://localhost:5173` (or similar)*

---

## 🔌 API Reference

### REST Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/history` | Fetch all past simulation runs and their results. |
| `DELETE` | `/history/{run_id}` | Delete a specific simulation run by ID. |

### WebSocket Protocol

**Endpoint**: `ws://localhost:8000/ws/simulate`

**Client -> Server (Start Config):**
```json
{
  "api_key": "gsk_...",
  "model_name": "llama3-8b-8192",
  "base_prompt": "You are a debt collector...",
  "max_cycles": 5,
  "batch_size": 1,
  "thresholds": {
    "repetition": 7.0,
    "negotiation": 8.0,
    "empathy": 6.0,
    "overall": 7.5
  }
}
```

**Server -> Client (Events):**
*   `{"type": "log", "message": "..."}`: Real-time system logs.
*   `{"type": "result", "transcript": "...", "score": 8.5, ...}`: Completed conversation result.
*   `{"type": "optimization", "new_prompt": "...", ...}`: Prompt update notification.

---

## 📖 Usage Guide

1.  **Configure Simulation**:
    *   Open the Dashboard.
    *   On the **Sidebar**, set your `Initial System Prompt` (defines the Agent's persona).
    *   Set **Targets**: Define the strict 1-10 scores required for Repetition, Negotiation, and Empathy.
    *   Select **Model**: Use `llama-3.1-8b-instant` for speed.

2.  **Start Optimization**:
    *   Click the **Start Optimization** button.
    *   The system will generate a "Defaulter" persona (e.g., "John, struggling with medical bills").
    *   The Agent and Defaulter will converse.

3.  **Monitor Progress**:
    *   **Live Stream**: Watch the conversation transcript appear in the center pane.
    *   **Logs**: View detailed system logs in the bottom-right terminal.
    *   **Optimization**: If the agent fails a scenario, the **Prompt Evolution** panel (top-right) will update with the *new, optimized prompt*, highlighting changes in Red/Green.

4.  **Review History**:
    *   Click the **History** card in the navbar.
    *   View past runs, seeing the exact prompt that was generated at each cycle.
    *   Click any scenario to open the **Detailed Modal** and see the full transcript and granular feedback.

---

## 📂 Project Structure

```bash
Odeon/
├── backend/
│   ├── main.py              # Entry point utilities
│   ├── server.py            # FastAPI & WebSocket server
│   ├── agent.py             # The AI Agent implementation
│   ├── simulator.py         # Conversation loop logic
│   ├── connections.py       # LLM Client Wrappers
│   ├── evaluator.py         # Grading & Scoring logic
│   ├── optimizer.py         # Prompt rewriting logic 
│   ├── history_manager.py   # SQLite database interaction
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Dashboard.tsx    # Main Layout
    │   │   ├── Sidebar.tsx      # Config Panel
    │   │   ├── LogTerminal.tsx  # System Logs
    │   │   ├── ScenarioCard.tsx # Result Display & Modal
    │   │   ├── UseHistory.tsx   # History Page
    │   │   └── DiffViewer.tsx   # Prompt Comparison
    │   ├── index.css            # Tailwind & Neumorphic styles
    │   └── main.tsx             # React Entry point
    └── package.json             # Node dependencies
```

---

## ⚖️ License

This project is licensed under the MIT License - see the `LICENSE` file for details.
