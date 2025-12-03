import argparse
import os
import sys

# --- Helper to read internal prompts ---
def get_internal_prompt(path_parts):
    """Reads a prompt file from within the expertflow package."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, *path_parts)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Could not find internal prompt at {file_path}")
        return ""

# --- Templates ---

# Read templates from the package source
ORCHESTRATOR_TEMPLATE = get_internal_prompt(["prompts", "orchestrator", "orch.md"])
TASK_PLANNER_TEMPLATE = get_internal_prompt(["prompts", "experts", "default", "task_planner_exp.md"])
MESSAGE_WRITER_TEMPLATE = get_internal_prompt(["prompts", "experts", "default", "msg_writer_exp.md"])
CUSTOM_EXPERT_TEMPLATE = get_internal_prompt(["prompts", "experts", "custom_template.md"])
CUSTOM_ORCHESTRATOR_TEMPLATE = get_internal_prompt(["prompts", "orchestrator", "custom_orch_template.md"])

MAIN_PY_TEMPLATE = """import os
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
"""

# --- CLI Logic ---

def init_project(project_name="."):
    """Initialize a new ExpertFlow project."""
    
    base_path = os.path.abspath(project_name)
    
    # Define structure
    dirs = [
        os.path.join(base_path, "prompts", "orchestrator"),
        os.path.join(base_path, "prompts", "experts"),
    ]
    
    files = {
        os.path.join(base_path, "prompts", "orchestrator", "orchestrator.md"): ORCHESTRATOR_TEMPLATE,
        os.path.join(base_path, "prompts", "experts", "task_planner.md"): TASK_PLANNER_TEMPLATE,
        os.path.join(base_path, "prompts", "experts", "message_writer.md"): MESSAGE_WRITER_TEMPLATE,
        os.path.join(base_path, "prompts", "experts", "custom_template.md"): CUSTOM_EXPERT_TEMPLATE,
        os.path.join(base_path, "prompts", "orchestrator", "custom_orch_template.md"): CUSTOM_ORCHESTRATOR_TEMPLATE,
        os.path.join(base_path, "main.py"): MAIN_PY_TEMPLATE,
    }

    print(f"🚀 Initializing ExpertFlow project in '{base_path}'...")

    # Create directories
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"   Created directory: {d}")

    # Create files
    for file_path, content in files.items():
        if os.path.exists(file_path):
            print(f"   Skipped (exists): {file_path}")
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"   Created file: {file_path}")

    print("\n✅ Project initialized successfully!")
    print("\nNext steps:")
    print("1. Set your GOOGLE_API_KEY environment variable.")
    print("If you don't have one, create one for free at https://aistudio.google.com/api-keys")
    print("2. Run the application: python main.py")

def main():
    parser = argparse.ArgumentParser(description="ExpertFlow CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new ExpertFlow project")
    init_parser.add_argument("name", nargs="?", default=".", help="Project name (directory)")

    args = parser.parse_args()

    if args.command == "init":
        init_project(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
