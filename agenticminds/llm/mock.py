from typing import List, Any, Dict
from ..types import Message
from .base import BaseLLM

class MockLLM(BaseLLM):
    """
    A Mock LLM for testing purposes.
    Returns predefined responses or echoes input.
    """
    def __init__(self, responses: Dict[str, str] = None, default_response: str = "Mock Response"):
        self.responses = responses or {}
        self.default_response = default_response
        self._last_usage = {"total": 0}

    def generate(self, messages: List[Message], system_prompt: str = None, tools: List[Any] = None, **kwargs) -> str:
        last_msg = messages[-1].content if messages else ""
        
        # Simple keyword matching for routing tests
        if "python" in last_msg.lower():
            return "python_tutor"
        if "math" in last_msg.lower():
            return "math_wizard"
            
        return self.responses.get(last_msg, self.default_response)

    def get_token_usage(self) -> Dict[str, int]:
        return {"total": 42}
