import os
import sys

# Add parent directory to path to import expertflow from source
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from expertflow import Agent, Router, ConversationManager
from expertflow.llm.gemini import GeminiLLM
from expertflow.utils import Colors

# 1. Load Prompts
def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Ensure you have your API key set

# uncomment below lines if using dotenv
# from dotenv import load_dotenv
# load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")

def main():
    # Paths to prompts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    orch_path = os.path.join(base_dir, "prompts", "orchestrator", "orchestrator.md")
    task_path = os.path.join(base_dir, "prompts", "experts", "task_planner.md")
    msg_path = os.path.join(base_dir, "prompts", "experts", "message_writer.md")

    # 2. Initialize Agents
    # Orchestrator
    orchestrator = Agent(
        name="Garvis",
        system_prompt=load_prompt(orch_path),
        description="Strategic Orchestrator and Productivity Manager."
    )

    # Experts
    task_planner = Agent(
        name="Task Planner",
        system_prompt=load_prompt(task_path),
        description="Expert in planning, prioritizing, and organizing tasks."
    )

    message_writer = Agent(
        name="Message Expert",
        system_prompt=load_prompt(msg_path),
        description="Expert in writing, editing, and refining messages."
    )

    # 3. Setup Router
    # The router manages the agents and the default entry point
    llm = GeminiLLM() # Or MockLLM() for testing
    
    router = Router(
        agents=[task_planner, message_writer],
        default_agent=orchestrator,
        llm=llm
    )

    # 4. Start Conversation
    manager = ConversationManager(router=router, llm=llm, debug=True)
    
    print("🤖 Garvis is ready! (Type 'quit' to exit)")
    print("-" * 50)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        response = manager.process_turn(user_id='01', message=user_input)
        # if agent switched, indicate it
        if response.switched_context:
            print(f"{Colors.GREEN}--- Switched to {response.agent_name} ---{Colors.ENDC}")
        print(f"Garvis {Colors.GREEN}({response.agent_name}){Colors.ENDC}: {response.content}")
        print("-" * 50)

if __name__ == "__main__":
    main()
