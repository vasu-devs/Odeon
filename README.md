# Self-Correcting Voice Agent Gym

An automated environment for testing, evaluating, and optimizing voice agent scripts.

## Components
- **DebtCollectionAgent**: The system under test (SUT).
- **DefaulterGenerater**: Creates realistic borrower personas.
- **ConversationSimulator**: Orchestrates the chat between Agent and Defaulter.
- **Evaluator**: Scores the agent on Repetition, Negotiation, and Empathy.
- **ScriptOptimizer**: Analyzes feedback and rewrites the Agent's prompt.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up Gemini API Key:
   - Create a `.env` file or set `GEMINI_API_KEY` in your terminal.
   ```bash
   export GEMINI_API_KEY="AIza..."
   ```

## Usage
Run the training loop:
```bash
python main.py --iterations 3
```

This will:
1. Generate a persona (e.g., "Aggressive Denier").
2. Simulate a conversation.
3. Evaluate the agent's performance.
4. Optimize the agent's prompt based on feedback.
5. Repeat for N iterations.
