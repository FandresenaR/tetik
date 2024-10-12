import cv2
import numpy as np
import base64
from PIL import Image
import io
import os
from openrouter_client import OpenRouterClient
import logging
from serpapi import GoogleSearch

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AICodingAssistant:
    _instance = None
    def __new__(cls, client=None):
        if cls._instance is None:
            cls._instance = super(AICodingAssistant, cls).__new__(cls)
            cls._instance.client = client if client else OpenRouterClient()
            logger.info(f"AICodingAssistant initialized with model: {cls._instance.get_current_model()}")
            if client is None:
                cls._instance.client = OpenRouterClient()
            else:
                cls._instance.client = client
            logger.info(f"AICodingAssistant initialized with model: {cls._instance.get_current_model()}")
        return cls._instance
    
    def __init__(self, client=None):
        if not hasattr(self, 'client'):
            self.client = client if client else OpenRouterClient()

    def process_text_input(self, text: str) -> dict:
        current_model = self.get_current_model()
        logger.info(f"Processing text input with model: {current_model}")
        try:
            model_specific_prompt = f"Respond to the following prompt without introducing yourself or stating your model name: {text}"
            response = self.client.chat_completion(model_specific_prompt)
            logger.debug(f"Raw response: {response}")
            return {"model": current_model, "content": response.strip()}
        except Exception as e:
            logger.exception("Error in process_text_input")
            return {"model": current_model, "content": f"Error: {str(e)}"}
    def process_image_input(self, image_path: str, user_question: str = "") -> dict:
        current_model = self.get_current_model()
        logger.info(f"Processing image input with model: {current_model}")
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            prompt = f"Respond to the following without introducing yourself or stating your model name: {user_question}\n[Image: data:image/jpeg;base64,{img_base64}]"
            response = self.client.chat_completion(prompt)
            logger.debug(f"Raw response: {response}")
            return {"model": current_model, "content": response.strip()}
        except Exception as e:
            logger.exception("Error in process_image_input")
            return {"model": current_model, "content": f"Error: {str(e)}"}
    def process_video_input(self, video_path: str, user_question: str = "") -> dict:
        current_model = self.get_current_model()
        logger.info(f"Processing video input with model: {current_model}")
        try:
            video = cv2.VideoCapture(video_path)
            success, frame = video.read()
            video.release()
            if not success:
                return {"model": current_model, "content": "Error: Unable to read the video file."}
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            prompt = f"Respond to the following without introducing yourself or stating your model name: {user_question}\n[Image: data:image/jpeg;base64,{img_base64}]"
            response = self.client.chat_completion(prompt)
            logger.debug(f"Raw response: {response}")
            return {"model": current_model, "content": response.strip()}
        except Exception as e:
            logger.exception("Error in process_video_input")
            return {"model": current_model, "content": f"Error: {str(e)}"}
    def search_online(self, query: str) -> list[dict]:
        logger.info(f"Searching online for query: {query}")
        try:
            # Get the API key from an environment variable or from the OpenRouterClient
            api_key = os.getenv("SERPAPI_API_KEY") or getattr(self.client, 'serpapi_key', None)
            logger.debug(f"API key retrieved: {'Yes' if api_key else 'No'}")

            if not api_key:
                raise ValueError("SERPAPI_API_KEY is not set")

            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key
            }
            logger.debug(f"SERP API params: {params}")
            
            logger.info("Initiating GoogleSearch")
            search = GoogleSearch(params)
            
            logger.info("Getting search results")
            results = search.get_dict()
            logger.debug(f"Raw SERP API results: {results}")
            
            if not results or 'error' in results:
                logger.error(f"Error in SERP API response: {results.get('error', 'Unknown error')}")
                return [{"title": "Error", "snippet": f"SERP API error: {results.get('error', 'Unknown error')}", "link": ""}]

            formatted_results = []
            organic_results = results.get("organic_results", [])
            logger.info(f"Number of organic results: {len(organic_results)}")

            for result in organic_results[:5]:  # Limit to top 5 results
                formatted_results.append({
                    "title": result.get("title", "No title"),
                    "snippet": result.get("snippet", "No snippet"),
                    "link": result.get("link", "No link")
                })
            
            logger.info(f"Formatted {len(formatted_results)} search results")
            return formatted_results
        except ValueError as ve:
            logger.error(f"ValueError in search_online: {ve}")
            return [{"title": "Error", "snippet": str(ve), "link": ""}]
        except Exception as e:
            logger.exception("Unexpected error in search_online")
            return [{"title": "Error", "snippet": f"An unexpected error occurred: {str(e)}", "link": ""}]

    def set_model(self, model: str) -> None:
        logger.info(f"Setting model to: {model}")
        self.client.set_model(model)
        logger.info(f"Model after setting: {self.get_current_model()}")
    def get_current_model(self) -> str:
        current_model = self.client.get_current_model()
        logger.debug(f"AICodingAssistant.get_current_model() returned: {current_model}")
        return current_model

    def get_available_models(self) -> list:
        return self.client.get_available_models()
