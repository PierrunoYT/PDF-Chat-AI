import requests
import os
from typing import List, Dict, Any

class OpenRouterClient:
    def __init__(self, api_key: str = None, site_url: str = None, site_name: str = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set it as an environment variable OPENROUTER_API_KEY or pass it to the constructor.")
        self.base_url = "https://openrouter.ai/api/v1"
        self.site_url = site_url
        self.site_name = site_name

    def chat_completion(self, messages: List[Dict[str, str]], model: str = "anthropic/claude-3.5-sonnet") -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter.

        :param messages: List of message dictionaries
        :param model: The model to use for completion
        :return: The API response as a dictionary
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
            "messages": messages
        }

        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def generate_embedding(self, text: str, model: str = "openai/text-embedding-ada-002") -> List[float]:
        """
        Generate an embedding for the given text using OpenRouter.

        :param text: The input text to embed
        :param model: The model to use for embedding
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
            "input": text
        }

        response = requests.post(f"{self.base_url}/embeddings", headers=headers, json=data)
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]
