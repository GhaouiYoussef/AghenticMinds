# ExpertFlow AI 🔀

**ExpertFlow AI** is a lightweight Python library for building multi-persona AI agents. It solves the "State Management" problem in conversational AI by providing a robust mechanism to:

1.  **Route** user intent to the correct "Expert" (Persona).
2.  **Manage** conversation history, ensuring context is preserved during handoffs.
3.  **Optimize** context windows by pruning stale system prompts and hints.

## Features

*   **Dynamic Router:** Hot-swap system prompts based on user intent classification.
*   **Context Pruning:** Automatically sanitizes chat history to save tokens and reduce hallucinations.
*   **Framework Agnostic:** Designed to work with any LLM provider (Google Gemini, OpenAI, Anthropic), though currently optimized for Google GenAI.

## Memory Optimization Strategy

To handle long-running conversations efficiently, ExpertFlow implements a **Dynamic History Compression** strategy. This ensures that the context window remains manageable without losing critical information.

### Mathematical Model

Let $H_t$ be the conversation history at turn $t$, and $|H_t|$ be its token count.
Let $\theta$ be the maximum token threshold (e.g., 100,000 tokens).
Let $H_{recent}$ be the set of $k$ most recent messages that must remain verbatim.
Let $H_{old} = H_t \setminus H_{recent}$ be the compressible history.

When $|H_t| > \theta$, the optimization function $f(H_t)$ is triggered:

$$
f(H_t) = S(H_{old}, r) \cup H_{recent}
$$

Where:
*   $S(text, r)$ is a summarization function that compresses text by a ratio $r$ (e.g., $r=4$ implies 10,000 tokens $\to$ 2,500 tokens).
*   The new token count becomes $|f(H_t)| \approx \frac{|H_{old}|}{r} + |H_{recent}|$.

This approach allows the system to maintain an "infinite" conversation loop where the oldest details are progressively compressed while the immediate context remains high-resolution.

## Installation

```bash
pip install expertflow-ai
```

## CLI Usage

ExpertFlow comes with a CLI to quickly scaffold new projects with best-practice templates.

```bash
# Initialize a new project
expertflow init my_agent_project

# Navigate to the project
cd my_agent_project

# Run the agent
python main.py
```

This generates a folder structure with:
*   `main.py`: The entry point for your agent.
*   `prompts/`: Directory containing system prompts for the Orchestrator and Experts.

## Quick Start

```python
from expertflow import Agent, Router, ConversationManager, GeminiLLM

# 1. Define your Agents
orchestrator = Agent(
    name="orchestrator",
    system_prompt="You are a helpful assistant. Route complex queries to experts.",
    description="General queries, greetings, and routing."
)

marketing_expert = Agent(
    name="marketing",
    system_prompt="You are a marketing guru. Focus on growth and SEO.",
    description="Questions about marketing, SEO, and growth."
)

# 2. Initialize Router
router = Router(agents=[orchestrator, marketing_expert], default_agent=orchestrator)

# 3. Manage Conversation
# Set debug=True to see detailed routing logs and state changes
manager = ConversationManager(router=router, llm=GeminiLLM(), debug=True)

user_input = "How do I improve my SEO?"
response = manager.process_turn(message=user_input)

print(f"Agent: {response.agent_name}")
print(f"Reply: {response.content}")
```
