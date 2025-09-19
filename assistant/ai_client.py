#!/usr/bin/env python3
"""
AI Client
Handles communication with Ollama and AI model management.
"""

import sys
from typing import List, Dict, Any
import ollama


class AIClient:
    """Manages AI model interactions and communication with Ollama."""
    
    def __init__(self, model: str = "llama3.2:3B"):
        self.model = model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Ollama client and test connection."""
        try:
            self.client = ollama.Client()
            # Test connection
            self.client.list()
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running and accessible.")
            sys.exit(1)
    
    def get_ai_response(self, messages: List[Dict[str, str]]) -> str:
        """Get AI response from Ollama with given messages."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=False
            )
            return response['message']['content']
        except Exception as e:
            return f"Error getting AI response: {e}"
    
    def change_model(self, new_model: str) -> str:
        """Change the AI model and verify it exists."""
        try:
            # Test if model exists
            models = self.client.list()
            available_models = [m['name'] for m in models['models']]
            if new_model in available_models:
                self.model = new_model
                return f"Model changed to {new_model}"
            else:
                return f"Model {new_model} not found. Available models: {', '.join(available_models)}"
        except Exception as e:
            return f"Error changing model: {e}"
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            models = self.client.list()
            return [m['name'] for m in models['models']]
        except Exception as e:
            print(f"Error getting available models: {e}")
            return []
    
    def get_model_info(self) -> str:
        """Get current model information."""
        return f"Current model: {self.model}"
