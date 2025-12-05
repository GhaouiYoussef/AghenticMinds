import os
import json
import datetime
from typing import Dict, List, Any, Optional
from .types import Expert, Message, TurnResponse
from .router import Router
from .memory import PNNet
from .llm.base import BaseLLM
from .utils import Colors

class Flow:
    def __init__(self, router: Router, llm: BaseLLM, debug: bool = False, optimize: bool = False):
        self.router = router
        self.llm = llm
        self.debug = debug
        self.optimize = optimize
            
        # In-memory storage for demo purposes. 
        # In production, this should be replaced by a persistent store (Redis/Mongo).
        self._sessions: Dict[str, Dict[str, Any]] = {} 
        
        # Ensure debug cache directory exists
        if self.debug:
            os.makedirs("debug-cache", exist_ok=True)

    def _get_session(self, user_id: str) -> Dict[str, Any]:
        if user_id not in self._sessions:
            self._sessions[user_id] = {
                "history": [],
                "current_expert": self.router.default_expert.name
            }
        return self._sessions[user_id]

    def _log_debug_memory(self, user_id: str, expert_name: str, history: List[Message]):
        """
        Logs the memory context to a file for debugging purposes.
        Overwrites the file for the same user to keep a single debug file.
        """
        if not self.debug:
            return

        filename = f"debug-cache/{user_id}_debug.json"
        
        try:
            # Convert Message objects to serializable dicts
            serializable_history = [msg.model_dump() for msg in history]
            
            # Wrap in a dict to include metadata since we removed it from filename
            debug_data = {
                "last_updated": datetime.datetime.now().isoformat(),
                "current_expert": expert_name,
                "history": serializable_history
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(debug_data, f, indent=2)
        except Exception as e:
            print(f"Debug Log Error: {e}")

    def process_turn(self, message: str, user_id: Optional[str] = None) -> TurnResponse:
        session = self._get_session(user_id)
        current_expert_name = session["current_expert"]
        history = session["history"]

        # 1. Classify / Route
        # Extract simple text history for the router
        text_history = [f"{m.role}: {m.content}" for m in history[-5:]]
        next_expert_name = self.router.classify(message, current_expert_name, text_history)
        
        switched = next_expert_name != current_expert_name
        if switched:

            print(f"{Colors.CYAN}--------Switched context from {current_expert_name} to {next_expert_name}------{Colors.ENDC}")
            # Prune history to remove old system prompts
            history = PNNet.sanitize_for_switch(history)
            session["current_expert"] = next_expert_name
            current_expert_name = next_expert_name

        current_expert = self.router.get_expert(current_expert_name)

        # 2. Prepare Context for LLM
        # We construct the messages list for the LLM
        
        # Note: In a real chat session, we might not want to append system prompt to history list permanently
        # but send it as part of the request.
        
        # 2.5 Debug Logging
        # We log the history before appending the new message for debugging state
        self._log_debug_memory(user_id, current_expert_name, history)

        # 3. Generate Response
        response_text = "Error: LLM not initialized."
        token_usage = {"total": 0}
        
        try:
            # Prepare messages for generation: History + New Message
            # We don't modify the persistent history yet
            messages_for_llm = history.copy()
            messages_for_llm.append(Message(role="user", content=message))
            
            response_text = self.llm.generate(
                messages=messages_for_llm,
                system_prompt=current_expert.system_prompt,
                tools=current_expert.tools
            )
            
            token_usage = self.llm.get_token_usage()

        except Exception as e:
            response_text = f"I encountered an error: {str(e)}"

        # 4. Update History
        # We append the user message and the assistant response to our internal history
        history.append(Message(role="user", content=message))
        history.append(Message(role="assistant", content=response_text))
        
        # Prune if too long
        session["history"] = PNNet.prune(history)

        # Summarize if optimize is enabled
        if self.optimize:
             session["history"] = PNNet.summarize_if_needed(session["history"], self.llm)

        return TurnResponse(
            content=response_text,
            agent_name=current_expert_name,
            switched_context=switched,
            token_usage=token_usage
        )
