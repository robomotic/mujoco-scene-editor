import os
import logging
from typing import List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """
    A client for OpenRouter LLM service, OpenAI-compatible.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("No OpenRouter API key found in OPENROUTER_API_KEY environment variable.")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://github.com/markusgrotz/mujoco-scene-editor",
                "X-Title": "MuJoCo Scene Editor",
            }
        )

    def query(self, builder, model: str = "google/gemini-flash-1.5-free"):
        """
        Query OpenRouter. For compatibility with the robits PromptBuilder, 
        we assume it has instructions that we can combine.
        """
        # If builder has instructions, use them. Otherwise, assume it's just a string or list.
        if hasattr(builder, "instructions"):
            prompt = "\n".join(builder.instructions)
        elif isinstance(builder, str):
            prompt = builder
        elif isinstance(builder, list):
            prompt = "\n".join(builder)
        else:
            prompt = str(builder)

        # Build messages. In this case, we'll just use a single role 'user' since 
        # it seems robits combines prefix and input into instructions.
        messages = [{"role": "user", "content": prompt}]

        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response

class PromptBuilderWrapper:
    """
    A simple wrapper for instructions similar to robits.vlm.openai_vlm.PromptBuilder
    """
    def __init__(self):
        self.instructions: List[str] = []

    def add_instruction(self, instruction: str):
        self.instructions.append(instruction)
