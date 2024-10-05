from ai_coding_assistant import AICodingAssistant
from openrouter_client import OpenRouterClient
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_model_persistence():
    # Create a single instance of OpenRouterClient
    client = OpenRouterClient()
    
    # Set a conservative max_tokens limit
    client.set_max_tokens(300)
    # Create an instance of AICodingAssistant with the shared client
    assistant = AICodingAssistant(client)
    
    # Test initial model
    logger.info(f"Initial model: {assistant.get_current_model()}")
    
    # Set model to GPT-4
    assistant.set_model("openai/gpt-4")
    logger.info(f"Model after setting to GPT-4: {assistant.get_current_model()}")
    
    # Process a text input
    response = assistant.process_text_input("What model are you? Please keep your answer very short.")
    logger.info(f"Response: {response}")
    
    # Set model to Mistral AI
    assistant.set_model("mistralai/mistral-7b-instruct:free")
    logger.info(f"Model after setting to Mistral AI: {assistant.get_current_model()}")
    
    # Process another text input
    response = assistant.process_text_input("What model are you now? Please keep your answer very short.")
    logger.info(f"Response: {response}")

    # Create a new instance of AICodingAssistant to test singleton behavior
    new_assistant = AICodingAssistant()
    logger.info(f"Model after creating new instance: {new_assistant.get_current_model()}")
if __name__ == "__main__":
    test_model_persistence()
