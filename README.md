# Odeon - AI Agent Optimization Platform

**Odeon** is an advanced AI testing and optimization platform designed to simulate, evaluate, and self-correct AI agent behaviors. It automates the loop of generating test scenarios, running conversations, scoring performance, and iteratively refining the system prompt to meet specific KPI targets.


[![Visualize in MapMyRepo](https://mapmyrepo.vasudev.live/badge.svg)](https://mapmyrepo.vasudev.live/?user=vasu-devs&repo=Odeon)

## 🚀 Key Features

*   **Autonomous Optimization Loop**: Automatically generates diverse user personas, runs simulations, evaluates performance, and rewrites the agent's prompt if KPIs are missed.
*   **Real-Time Simulation Stream**: Watch agent-user interactions unfold live via WebSockets.
*   **Prompt Evolution Diffing**: Visualizes exactly what changed in the system prompt between iterations (Red/Green diffs).
*   **Strict Monochrome UI**: A high-end, distraction-free "Neumorphic" interface designed for focus and clarity.
*   **Comprehensive Metrics**: Tracks Repetition, Negotiation, and Empathy scores with strict numeric thresholds.
*   **Simulation History**: Archives every run with full transcripts, scores, and evolved prompts for later analysis.
*   **Interactive Controls**: Adjustable thresholds, max cycles, and model selection (Llama 3 via Groq).

---

## 🛠️ Technology Stack

### Backend
*   **Python 3.10+**
*   **FastAPI**: High-performance async API framework.
*   **WebSockets**: For real-time bi-directional communication with the frontend.
*   **Groq API**: Ultra-fast inference for Llama 3 models (Agent & Simulator).
*   **LangChain / Pydantic**: Structured output generation and chain management.
*   **SQLite**: Local persistence for simulation history.

### Frontend
*   **React 19**: Modern UI library with Hooks.
*   **Vite**: Next-generation frontend tooling.
*   **TypeScript**: Type-safe development.
*   **Tailwind CSS 4**: Utility-first styling with custom Neumorphic utilities.
*   **Lucide React**: Minimalist icon set (replaced with custom SVGs in critical paths).

---

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

1.  **Python 3.10** or higher.
2.  **Node.js 18** or higher (and `npm`).
3.  **Groq API Key**: Get one from [console.groq.com](https://console.groq.com).

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
Create a `.env` file in the `backend/` directory:

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

```
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

## 🧩 Modifying the Agent

To change the core behavior or the type of simulation (e.g., changing from Debt Collection to Tech Support), modify:

1.  **Initial Prompt**: Change the text in the Sidebar on the frontend.
2.  **Persona Generator (`backend/personalities.py`)**: Update the prompts used to generate the "User" side of the conversation.
3.  **Evaluator (`backend/evaluator.py`)**: Update the scoring criteria (Rubric) to match your new domain.
