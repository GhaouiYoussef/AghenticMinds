# AgenticMinds

A lightweight library for multi-persona AI agent routing and state management.

## Features (v0.1)

*   **Flow**: Simple conversation management.
*   **Expert**: Define agents with specific personas and tools.
*   **Router**: Basic intent routing between experts.
*   **PNNet**: Tiny interface for memory optimization and context management.
*   **LLM Adapter**: Support for Gemini (and easy to extend).

## Installation

```bash
pip install agenticminds
```

## Usage Example

```python
import os
from agenticminds import Expert, Router, Flow
from agenticminds.llm import GeminiLLM

# 1. Setup LLM
# Ensure GOOGLE_API_KEY is set in your environment
llm = GeminiLLM(model_name="gemini-2.0-flash", api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Define Experts
support_expert = Expert(
    name="support",
    description="Handles technical support queries.",
    system_prompt="You are a technical support specialist. Help users with their issues."
)

sales_expert = Expert(
    name="sales",
    description="Handles sales inquiries and pricing.",
    system_prompt="You are a sales representative. Answer questions about pricing and features."
)

# 3. Setup Router
router = Router(
    experts=[support_expert, sales_expert],
    llm=llm
)

# 4. Create Flow
flow = Flow(router=router, llm=llm)

# 5. Run Conversation
response = flow.process_turn("I have a problem with my account.")
print(f"Agent: {response.agent_name}")
print(f"Response: {response.content}")

response = flow.process_turn("How much does the premium plan cost?")
print(f"Agent: {response.agent_name}")
print(f"Response: {response.content}")
```

## Advanced Quick Start

For a more complex scenario involving an **Orchestrator** that switches "modes" (personas) instead of transferring to different agents, check out the `advanced_example.py`.

This example demonstrates:
1.  **Orchestrator Persona**: A central guide ("Orion") who listens to the user.
2.  **Mode Switching**: The Orchestrator switches to "Sales Mode" or "Support Mode" based on intent.
3.  **Interactive Chat**: A loop to chat with the agent in real-time.

### Running the Advanced Example

1.  Ensure your `GOOGLE_API_KEY` is set in your `.env` file or environment variables.
2.  Run the script:

```bash
python advanced_example.py
```

3.  **Try it out**:
    *   Say "My app is crashing" -> Switches to **Support**.
    *   Say "I want to buy a license" -> Switches to **Sales**.

### Using Quick Start Prompts

You can access the pre-defined prompts used in the advanced example directly from the package:

```python
from agenticminds.prompts import QUICK_START_ORCHESTRATOR, QUICK_START_SALES, QUICK_START_SUPPORT

# Use them in your Expert definitions
orchestrator = Expert(
    name="orchestrator",
    description="Central Guide",
    system_prompt=QUICK_START_ORCHESTRATOR
)
```

