import cv2
import numpy as np
import base64
import requests
from PIL import Image
import io
from openrouter_client import OpenRouterClient
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AICodingAssistant:
    _instance = None
    def __new__(cls, client=None):
        if cls._instance is None:
            cls._instance = super(AICodingAssistant, cls).__new__(cls)
            if client is None:
                cls._instance.client = OpenRouterClient()
            else:
                cls._instance.client = client
            logger.info(f"AICodingAssistant initialized with model: {cls._instance.get_current_model()}")
        return cls._instance
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
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            results = []
            for result in data.get('RelatedTopics', [])[:5]:
                if 'Result' in result:
                    title = result['Text'].split(' - ')[0]
                    snippet = result['Text']
                    link = result.get('FirstURL', '')
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "link": link
                    })
            return results
        except Exception as e:
            logger.exception("Error in search_online")
            return [{"title": "Error", "snippet": str(e), "link": ""}]

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
