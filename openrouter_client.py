import requests
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set it in the .env file as OPENROUTER_API_KEY.")
        self.base_url = "https://openrouter.ai/api/v1"

    def chat_completion(self, messages: List[Dict[str, str]], model: str = "anthropic/claude-3.5-sonnet") -> str:
        """
        Send a chat completion request to OpenRouter.

        :param messages: List of message dictionaries
        :param model: The model to use for completion
        :return: The generated response as a string
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        

        data = {
            "model": model,
            "messages": messages
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def generate_embedding(self, text: str, model: str = "openai/text-embedding-3-small", dimensions: int = 1536) -> List[float]:
        """
        Generate an embedding for the given text using OpenRouter.

        :param text: The input text to embed
        :param model: The model to use for embedding
        :param dimensions: The number of dimensions for the embedding (default: 1536)
        :return: The embedding as a list of floats
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            headers["X-Title"] = self.site_name

        data = {
            "model": model,
            "input": text,
            "dimensions": dimensions
        }

        response = requests.post(f"{self.base_url}/embeddings", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
