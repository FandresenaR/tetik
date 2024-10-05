import cv2
import numpy as np
import base64
import requests
from PIL import Image
import io
from openrouter_client import OpenRouterClient
class AICodingAssistant:
    def __init__(self):
        self.client = OpenRouterClient()
    def process_text_input(self, text):
        return self.client.chat_completion(text)
    def process_image_input(self, image_path, user_question=""):
        # Convert image to base64
        with Image.open(image_path) as img:
            img = img.convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        prompt = f"{user_question}\n[Image: data:image/jpeg;base64,{img_base64}]"
        return self.client.chat_completion(prompt)
    def process_video_input(self, video_path, user_question=""):
        # For simplicity, analyze the first frame
        video = cv2.VideoCapture(video_path)
        success, frame = video.read()
        video.release()

        if not success:
            return "Error: Unable to read the video file."

        # Convert frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        prompt = f"{user_question}\n[Image: data:image/jpeg;base64,{img_base64}]"
        return self.client.chat_completion(prompt)
    def search_online(self, query):
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url)
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
