import os
import requests
from dotenv import load_dotenv

load_dotenv()
class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def chat_completion(self, prompt, use_middle_out=False):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }
        if use_middle_out:
            data["transforms"] = ["middle-out"]
        response = requests.post(self.api_url, headers=headers, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content']
            elif 'error' in response_data:
                if 'maximum context length' in response_data['error']['message'] and not use_middle_out:
                    print("Token limit exceeded. Retrying with middle-out transform...")
                    return self.chat_completion(prompt, use_middle_out=True)
                return f"Error: {response_data['error']['message']}"
            else:
                return f"Error: Unexpected response structure. Full response: {response_data}"
        else:
            return f"Error: {response.status_code} - {response.text}"

def generate_response(prompt):
    client = OpenRouterClient()
    return client.chat_completion(prompt)
# Example usage
user_input = "What is the meaning of life?"
ai_response = generate_response(user_input)
print(ai_response)
