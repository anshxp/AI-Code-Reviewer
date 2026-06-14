"""NanoBanana image generation service."""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImageResult:
    success: bool
    image_data: bytes | None = None
    error: str | None = None


class NanoBananaService:
    """Service to generate images using NanoBanana AI API."""
    
    # NanoBanana API endpoint - supports both free and paid tiers
    API_URL = "https://api.nanobanana.ai/v1/image"
    CACHE_DIR = Path.home() / ".cache" / "mini-ai-images"
    
    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize the NanoBanana service.
        
        Args:
            api_key: API key for NanoBanana (or None to use NANOBANANA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("NANOBANANA_API_KEY", "")
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def generate_image(self, prompt: str, cache_key: str | None = None, width: int = 512, height: int = 512) -> ImageResult:
        """
        Generate an image from a text prompt using NanoBanana API.
        
        Args:
            prompt: Text description for the image
            cache_key: Optional cache key (if None, uses hash of prompt)
            width: Image width (default 512)
            height: Image height (default 512)
        
        Returns:
            ImageResult with success status and image data
        """
        if cache_key is None:
            cache_key = str(hash(prompt) % (10**8))
        
        cache_path = self.CACHE_DIR / f"{cache_key}.png"
        if cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    return ImageResult(success=True, image_data=f.read())
            except Exception as e:
                return ImageResult(success=False, error=f"Cache read failed: {e}")
        
        try:
            image_data = self._call_nanobanana_api(prompt, width, height)
            
            # Cache the image
            try:
                with open(cache_path, "wb") as f:
                    f.write(image_data)
            except Exception:
                pass  # Cache failure is not critical
            
            return ImageResult(success=True, image_data=image_data)
        except Exception as e:
            return ImageResult(success=False, error=str(e))
    
    def _call_nanobanana_api(self, prompt: str, width: int, height: int) -> bytes:
        """
        Make a real HTTP request to the NanoBanana API.
        
        Args:
            prompt: The image prompt
            width: Image width
            height: Image height
        
        Returns:
            PNG image data as bytes
        
        Raises:
            Exception: If API call fails
        """
        request_body = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "model": "stable-diffusion-v1-5",  # or another supported model
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        json_data = json.dumps(request_body).encode("utf-8")
        
        req = urllib.request.Request(
            self.API_URL,
            data=json_data,
            headers=headers,
            method="POST",
        )
        
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                
                # NanoBanana API returns base64-encoded image
                if "image" in response_data:
                    import base64
                    image_base64 = response_data["image"]
                    return base64.b64decode(image_base64)
                else:
                    raise ValueError("No image in API response")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"NanoBanana API error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error connecting to NanoBanana: {e.reason}")
