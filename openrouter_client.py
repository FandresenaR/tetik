import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List
import logging
from serpapi import GoogleSearch

load_dotenv()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class OpenRouterClient:
    def __init__(self):
        self.api_key: str = os.getenv("OPENROUTER_API_KEY", "")
        self.serpapi_key = os.environ.get("SERPAPI_API_KEY")
        logger.debug(f"SERP API key initialized: {'Yes' if self.serpapi_key else 'No'}")
        self.api_url: str = "https://openrouter.ai/api/v1/chat/completions"
        self.available_models: List[str] = [
            "openai/gpt-3.5-turbo",
            "meta-llama/llama-3.2-11b-vision-instruct:free",
            "google/palm-2-chat-bison",
            "deepseek/deepseek-chat",
            "mistralai/mistral-7b-instruct:free",
            "liquid/lfm-40b:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "google/gemini-flash-1.5-8b-exp",
            "meta-llama/llama-3.1-405b-instruct:free",
            "qwen/qwen-2-7b-instruct:free",
            "microsoft/phi-3-medium-128k-instruct:free",
            "gryphe/mythomist-7b:free",
            "openchat/openchat-7b:free",
            "undi95/toppy-m-7b:free",
            "huggingfaceh4/zephyr-7b-beta:free",
            "google/gemma-2-9b-it:free",
        ]
        self.current_model: str = self.available_models[0]
        self.max_tokens: int = 500  # Set a conservative default
        logger.debug(f"OpenRouterClient initialized with model: {self.current_model}")
    def set_model(self, model: str) -> None:
        if model in self.available_models:
            self.current_model = model
            logger.info(f"Model set to: {self.current_model}")
        else:
            logger.warning(f"Invalid model: {model}. Using default: {self.current_model}")

    def chat_completion(self, prompt: str, use_middle_out: bool = False) -> str:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/yourproject",  # Replace with your actual GitHub repo
            "X-Title": "Your Project Name"  # Replace with your project name
        }
        data: Dict[str, Any] = {
            "model": self.current_model,
            "messages": [
                {"role": "system", "content": f"You are {self.current_model}. Always respond as if you are this specific model."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens
        }
        if use_middle_out:
            data["transforms"] = ["middle-out"]
        try:
            logger.info(f"Sending request to OpenRouter API with model: {self.current_model}")
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            logger.debug(f"Raw API response: {response_data}")
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content']
            else:
                return f"Error: Unexpected response structure. Full response: {response_data}"
        except requests.exceptions.RequestException as e:
            if 'maximum context length' in str(e) and not use_middle_out:
                logger.warning("Token limit exceeded. Retrying with middle-out transform...")
                return self.chat_completion(prompt, use_middle_out=True)
            logger.exception("Error in chat_completion")
            return f"Error: {str(e)}"
    def get_available_models(self) -> List[str]:
        return self.available_models

    def get_current_model(self) -> str:
        logger.debug(f"Current model: {self.current_model}")
        return self.current_model

    def set_max_tokens(self, max_tokens: int) -> None:
        self.max_tokens = max_tokens
        logger.info(f"Max tokens set to: {self.max_tokens}")

    def search_web(self, query):
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        organic_results = results.get("organic_results", [])
        formatted_results = []

        for result in organic_results[:5]:  # Limit to top 5 results
            formatted_results.append({
                "title": result.get("title"),
                "snippet": result.get("snippet"),
                "link": result.get("link")
            })

        return formatted_results