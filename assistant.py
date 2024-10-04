import os
import requests
import cv2
import pytesseract
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from file_utils import select_image_from_folder
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = os.getenv("SITE_URL", "https://aicodingassistant.com")
SITE_NAME = os.getenv("SITE_NAME", "AICodingAssistant")

class AICodingAssistant:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
            "Content-Type": "application/json"
        }
        print(f"API Key: {OPENROUTER_API_KEY}")  # Debug print
        print(f"Headers: {self.headers}")  # Debug print

    def generate_response(self, prompt):
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.json()['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
            return f"Error: Unable to generate response. Status code: {response.status_code}"
        except Exception as err:
            print(f"An error occurred: {err}")
            return "Error: Unable to generate response due to an unexpected error."

    def process_text_input(self, text):
        prompt = f"As an AI coding assistant, please respond to the following: {text}"
        return self.generate_response(prompt)

    def process_image_input(self, image_path):
        img = cv2.imread(image_path)
        text = pytesseract.image_to_string(img)
        prompt = f"As an AI coding assistant, analyze the following text extracted from an image: {text}"
        return self.generate_response(prompt)

    def process_video_input(self, video_url):
        video_id = video_url.split("v=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        prompt = f"As an AI coding assistant, summarize and analyze the following video transcript: {text}"
        return self.generate_response(prompt)

    def search_online(self, query):
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('div', class_='g')
        
        extracted_info = []
        for result in search_results[:3]:
            title = result.find('h3', class_='r')
            link = result.find('a')
            snippet = result.find('div', class_='s')
            if title and link and snippet:
                extracted_info.append({
                    'title': title.text,
                    'link': link['href'],
                    'snippet': snippet.text
                })
        return extracted_info

# Example usage
if __name__ == "__main__":
    assistant = AICodingAssistant()
    
    # Example of processing text input
    text_response = assistant.process_text_input("How to implement quicksort in Python?")
    print("Text response:", text_response)
    
    # Example of processing image input
    image_response = assistant.process_image_input("path/to/image.jpg")
    print("Image response:", image_response)
