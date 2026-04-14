"""
AI Model Service for content generation
Interfaces with Ollama for LLMs and HuggingFace for other models
"""
import httpx
import asyncio
import json
from typing import Optional, List
from loguru import logger
from src.config import settings


class AIModelService:
    """Manages interactions with AI models"""
    
    def __init__(self):
        self.ollama_url = settings.OLLAMA_API_URL
        self.hf_api_key = settings.HUGGINGFACE_API_KEY
        self.text_model = settings.TEXT_GENERATION_MODEL
        self.image_model = settings.IMAGE_MODEL
        self.tts_model = settings.TTS_MODEL
    
    async def generate_text(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        """
        Generate text using LLaMA/Mistral via Ollama
        Falls back to HuggingFace API if Ollama unavailable
        """
        try:
            # Try local Ollama first
            url = f"{self.ollama_url}/api/generate"
            
            payload = {
                "model": self.text_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": settings.TEXT_MODEL_TEMPERATURE,
                    "top_p": settings.TEXT_MODEL_TOP_P,
                    "num_predict": max_tokens
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("response", "").strip()
                    logger.info(f"Generated text via Ollama ({len(text)} chars)")
                    return text
        
        except Exception as e:
            logger.warning(f"Ollama unavailable: {e}, trying HuggingFace")
        
        # Fallback to HuggingFace Inference API
        return await self._generate_text_huggingface(prompt, max_tokens)
    
    async def _generate_text_huggingface(self, prompt: str, max_tokens: int = 512) -> Optional[str]:
        """Generate text using HuggingFace API"""
        try:
            if not self.hf_api_key:
                logger.error("HuggingFace API key not configured")
                return None
            
            url = f"https://api-inference.huggingface.co/models/{self.text_model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_tokens,
                    "temperature": settings.TEXT_MODEL_TEMPERATURE
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        text = result[0].get("generated_text", "").strip()
                        logger.info(f"Generated text via HuggingFace ({len(text)} chars)")
                        return text
        
        except Exception as e:
            logger.error(f"Failed to generate text from HuggingFace: {e}")
        
        return None
    
    async def generate_image(self, prompt: str, width: int = 1080, height: int = 1920) -> Optional[str]:
        """
        Generate image using Stable Diffusion
        Returns URL to generated image
        """
        try:
            if settings.IMAGE_GENERATION_API == "huggingface":
                return await self._generate_image_huggingface(prompt, width, height)
            else:
                logger.error(f"Unsupported image generation API: {settings.IMAGE_GENERATION_API}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            return None
    
    async def _generate_image_huggingface(self, prompt: str, width: int, height: int) -> Optional[str]:
        """Generate image via HuggingFace Inference API"""
        try:
            if not self.hf_api_key:
                logger.error("HuggingFace API key not configured")
                return None
            
            url = f"https://api-inference.huggingface.co/models/{self.image_model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "width": width,
                    "height": height,
                    "num_inference_steps": 50
                }
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    # Response is image bytes
                    # In production, upload to S3 and return URL
                    logger.info(f"Generated image via HuggingFace ({len(response.content)} bytes)")
                    return f"data:image/png;base64,{response.content.hex()[:50]}..."
        
        except Exception as e:
            logger.error(f"Failed to generate image from HuggingFace: {e}")
        
        return None
    
    async def generate_speech(self, text: str, voice_id: str = "default") -> Optional[str]:
        """
        Generate speech/audio from text
        Uses Coqui TTS or similar service
        """
        try:
            # This would typically call a TTS service
            # For now, return a mock implementation
            logger.info(f"Generating speech for: {text[:50]}...")
            
            # In production, would use:
            # - Local Coqui TTS
            # - ElevenLabs API
            # - Google Cloud TTS
            # - Azure Speech Services
            
            return "https://example.com/speech.mp3"
        
        except Exception as e:
            logger.error(f"Failed to generate speech: {e}")
            return None
    
    async def batch_generate_text(self, prompts: List[str]) -> List[Optional[str]]:
        """Generate text for multiple prompts concurrently"""
        tasks = [self.generate_text(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
    
    async def batch_generate_images(self, prompts: List[str]) -> List[Optional[str]]:
        """Generate images for multiple prompts concurrently"""
        tasks = [self.generate_image(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)


# Global AI model service instance
ai_service = AIModelService()
