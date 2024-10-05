import cv2
import numpy as np
import base64
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
    def process_text_input(self, text: str) -> str:
        current_model = self.get_current_model()
        logger.info(f"Processing text input with model: {current_model}")
        try:
            model_specific_prompt = f"Remember, you are {current_model}. Please respond to the following prompt: {text}"
            response = self.client.chat_completion(model_specific_prompt)
            logger.debug(f"Raw response: {response}")
            return f"[Model: {current_model}]\n\n{response}"
        except Exception as e:
            logger.exception("Error in process_text_input")
            return f"Error: {str(e)}"

    def process_image_input(self, image_path: str, user_question: str = "") -> str:
        current_model = self.get_current_model()
        logger.info(f"Processing image input with model: {current_model}")
        try:
            with Image.open(image_path) as img:
                img = img.convert('RGB')
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            prompt = f"You are {current_model}. First, state 'I am {current_model}.' Then, respond to the following: {user_question}\n[Image: data:image/jpeg;base64,{img_base64}]"
            response = self.client.chat_completion(prompt)
            logger.debug(f"Raw response: {response}")
            return f"[Model: {current_model}]\n\n{response}"
        except Exception as e:
            logger.exception("Error in process_image_input")
            return f"Error: {str(e)}"
    def process_video_input(self, video_path: str, user_question: str = "") -> str:
        current_model = self.get_current_model()
        logger.info(f"Processing video input with model: {current_model}")
        try:
            video = cv2.VideoCapture(video_path)
            success, frame = video.read()
            video.release()
            if not success:
                return "Error: Unable to read the video file."
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            prompt = f"You are {current_model}. First, state 'I am {current_model}.' Then, respond to the following: {user_question}\n[Image: data:image/jpeg;base64,{img_base64}]"
            response = self.client.chat_completion(prompt)
            logger.debug(f"Raw response: {response}")
            return f"[Model: {current_model}]\n\n{response}"
        except Exception as e:
            logger.exception("Error in process_video_input")
            return f"Error: {str(e)}"
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
