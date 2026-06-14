"""Google Gemini AI integration for image generation and explanations."""
from __future__ import annotations

import json
import os
import base64
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path


def load_env_file() -> None:
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


@dataclass
class ImageResult:
    success: bool
    image_data: bytes | None = None
    error: str | None = None


@dataclass
class ExplanationResult:
    success: bool
    text: str = ""
    error: str | None = None


class GeminiService:
    """Service to generate images and explanations using Google Gemini AI."""
    
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    TEXT_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    CACHE_DIR = Path.home() / ".cache" / "mini-ai-images"
    
    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize Gemini service.
        
        Args:
            api_key: Google Gemini API key (or None to use GEMINI_API_KEY env var)
        """
        load_env_file()  # Load from .env file first
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_image_description(self, prompt: str, cache_key: str | None = None) -> ImageResult:
        """
        Generate an image description using Gemini that can be visualized.
        Since Gemini doesn't directly generate images, we create ASCII art or use it to
        describe what the visualization should look like, then render it.
        
        Args:
            prompt: Text description for visualization
            cache_key: Optional cache key
        
        Returns:
            ImageResult with success status
        """
        if cache_key is None:
            cache_key = str(hash(prompt) % (10**8))
        
        cache_path = self.CACHE_DIR / f"{cache_key}.txt"
        if cache_path.exists():
            try:
                with open(cache_path, "r") as f:
                    return ImageResult(success=True, image_data=f.read().encode())
            except Exception as e:
                return ImageResult(success=False, error=f"Cache read failed: {e}")
        
        try:
            # Get Gemini to create a visual description
            description = self._call_gemini_text(
                f"Create a detailed ASCII art diagram for: {prompt}\n\n"
                "Make it educational and visually appealing. Use ASCII characters to create boxes, "
                "arrows, and labels. Keep it under 20 lines. Focus on clarity for beginners."
            )
            
            if description.success:
                try:
                    with open(cache_path, "w") as f:
                        f.write(description.text)
                except Exception:
                    pass
                
                return ImageResult(success=True, image_data=description.text.encode())
            else:
                return description
        except Exception as e:
            return ImageResult(success=False, error=str(e))
    
    def generate_explanation(self, title: str, message: str, fix: str) -> ExplanationResult:
        """
        Generate a comprehensive explanation using Gemini.
        
        Args:
            title: Error title
            message: Error message
            fix: How to fix it
        
        Returns:
            ExplanationResult with generated text
        """
        try:
            prompt = f"""Generate a beginner-friendly explanation for this Python coding error:

Title: {title}
What happened: {message}
How to fix: {fix}

Please provide:
1. A simple explanation (2-3 sentences)
2. Why this matters (1-2 sentences)
3. A quick example of correct code (code block)
4. Key concept to remember (1 sentence)

Format it clearly and make it suitable for a beginner programmer."""
            
            result = self._call_gemini_text(prompt)
            return result
        except Exception as e:
            return ExplanationResult(success=False, error=str(e))
    
    def _call_gemini_text(self, prompt: str) -> ExplanationResult:
        """Make a request to Gemini text API."""
        if not self.api_key:
            return ExplanationResult(
                success=False,
                error="GEMINI_API_KEY not set. Set it with: export GEMINI_API_KEY='your-key'"
            )
        
        request_body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        url = f"{self.TEXT_API_URL}?key={self.api_key}"
        
        json_data = json.dumps(request_body).encode("utf-8")
        
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                
                if "candidates" in response_data and response_data["candidates"]:
                    text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    return ExplanationResult(success=True, text=text)
                else:
                    return ExplanationResult(
                        success=False,
                        error="No response from Gemini"
                    )
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            return ExplanationResult(
                success=False,
                error=f"Gemini API error {e.code}: {error_body}"
            )
        except urllib.error.URLError as e:
            return ExplanationResult(
                success=False,
                error=f"Network error: {e.reason}"
            )
