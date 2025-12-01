import unittest
from unittest.mock import MagicMock, patch
import sys

# Ensure we can import the package
sys.path.append(".")

from expertflow import Agent, Router, ConversationManager, Message

class TestAgents(unittest.TestCase):
    def setUp(self):
        self.agent1 = Agent(
            name="math_expert",
            description="Expert in math",
            system_prompt="You are a math expert."
        )
        self.agent2 = Agent(
            name="python_expert",
            description="Expert in python",
            system_prompt="You are a python expert."
        )
        self.agents = [self.agent1, self.agent2]

    def test_agent_initialization(self):
        agent = Agent(
            name="test",
            description="desc",
            system_prompt="prompt"
        )
        self.assertEqual(agent.name, "test")
        self.assertEqual(agent.description, "desc")
        self.assertEqual(agent.system_prompt, "prompt")
        self.assertEqual(agent.model_name, "gemini-2.0-flash") # Default

    @patch("expertflow.router.genai")
    def test_router_classification(self, mock_genai):
        # Setup mock
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        
        # Mock response for classification
        mock_response = MagicMock()
        mock_response.text = "python_expert"
        mock_client.models.generate_content.return_value = mock_response

        router = Router(agents=self.agents, default_agent=self.agent1, api_key="dummy")
        
        # Test classification
        result = router.classify("Help me with python code", "math_expert")
        
        self.assertEqual(result, "python_expert")
        mock_client.models.generate_content.assert_called_once()

    @patch("expertflow.session.genai")
    @patch("expertflow.router.genai")
    def test_conversation_flow(self, mock_router_genai, mock_session_genai):
        # Setup mocks
        mock_router_client = MagicMock()
        mock_router_genai.Client.return_value = mock_router_client
        
        mock_session_client = MagicMock()
        mock_session_genai.Client.return_value = mock_session_client
        
        # Mock Router classification to switch agent
        mock_router_response = MagicMock()
        mock_router_response.text = "python_expert"
        mock_router_client.models.generate_content.return_value = mock_router_response

        # Mock Session chat response
        mock_chat = MagicMock()
        mock_chat_response = MagicMock()
        mock_chat_response.text = "Here is some python code."
        mock_chat_response.usage_metadata.total_token_count = 10
        mock_chat.send_message.return_value = mock_chat_response
        mock_session_client.chats.create.return_value = mock_chat

        # Initialize
        router = Router(agents=self.agents, default_agent=self.agent1, api_key="dummy")
        manager = ConversationManager(router=router, api_key="dummy")

        # Test process_turn
        response = manager.process_turn("user1", "Write a python script")

        # Verify switch happened
        self.assertTrue(response.switched_context)
        self.assertEqual(response.agent_name, "python_expert")
        self.assertEqual(response.content, "Here is some python code.")
        
        # Verify history update
        session_data = manager._get_session("user1")
        self.assertEqual(len(session_data["history"]), 2) # User msg + Assistant msg
        self.assertEqual(session_data["history"][0].content, "Write a python script")
        self.assertEqual(session_data["history"][1].content, "Here is some python code.")

    @patch("expertflow.session.genai")
    @patch("expertflow.router.genai")
    def test_no_switch_flow(self, mock_router_genai, mock_session_genai):
        # Setup mocks
        mock_router_client = MagicMock()
        mock_router_genai.Client.return_value = mock_router_client
        
        mock_session_client = MagicMock()
        mock_session_genai.Client.return_value = mock_session_client
        
        # Mock Router classification to STAY on same agent
        mock_router_response = MagicMock()
        mock_router_response.text = "math_expert" # Same as default
        mock_router_client.models.generate_content.return_value = mock_router_response

        # Mock Session chat response
        mock_chat = MagicMock()
        mock_chat_response = MagicMock()
        mock_chat_response.text = "2 + 2 is 4."
        mock_chat.send_message.return_value = mock_chat_response
        mock_session_client.chats.create.return_value = mock_chat

        # Initialize
        router = Router(agents=self.agents, default_agent=self.agent1, api_key="dummy")
        manager = ConversationManager(router=router, api_key="dummy")

        # Test process_turn
        response = manager.process_turn("user1", "What is 2+2?")

        # Verify NO switch
        self.assertFalse(response.switched_context)
        self.assertEqual(response.agent_name, "math_expert")
        self.assertEqual(response.content, "2 + 2 is 4.")

if __name__ == "__main__":
    unittest.main()
