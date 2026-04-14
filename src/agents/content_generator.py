"""
Content Generation Agents
Uses Microsoft Agent Framework to orchestrate content creation pipeline
"""
from agent_framework import Executor, handler, WorkflowContext, WorkflowBuilder
from typing import Optional, List
from loguru import logger
from src.config import settings
from src.models import ContentScript, ContentNiche, Platform, ContentPiece
from src.services.ai_models import ai_service
from datetime import datetime
import uuid


# ============= CONTENT STRATEGY AGENT =============
class ContentStrategyExecutor(Executor):
    """
    Analyzes trends and generates content hooks/strategies
    Responsible for: topic research, hook generation, angle selection
    """
    
    def __init__(self, id: str = "content_strategy"):
        super().__init__(id=id)
    
    @handler
    async def generate_strategy(self, niche: ContentNiche, ctx: WorkflowContext[dict]) -> None:
        """Generate content strategy for a niche"""
        try:
            logger.info(f"Generating strategy for niche: {niche.value}")
            
            # Generate hook using AI
            hook_prompt = f"""
            Create a compelling hook for a {niche.value} content piece.
            Requirements:
            - Start with curiosity gap or pattern interrupt
            - 5-15 words maximum
            - Include emotional trigger
            - End with question or scenario
            
            Examples for reference:
            - "You've been doing [task] wrong your whole life"
            - "Nobody talks about this [fact] but it's true"
            - "[Demographic] when [situation]"
            - "This [thing] will change how you think about [topic]"
            
            Generate a unique hook that hasn't been done before.
            Output: Just the hook text, nothing else.
            """
            
            hook = await ai_service.generate_text(hook_prompt, max_tokens=50)
            
            strategy = {
                "niche": niche.value,
                "hook": hook or "Default hook if generation fails",
                "target_audience": "general",
                "platforms": ["tiktok", "instagram_reels", "youtube_shorts"],
                "keywords": self._get_keywords_for_niche(niche),
                "tone": "engaging",
                "duration_seconds": 60
            }
            
            await ctx.send_message(strategy)
            
        except Exception as e:
            logger.error(f"Failed to generate strategy: {e}")
            await ctx.send_message({"error": str(e)})
    
    @staticmethod
    def _get_keywords_for_niche(niche: ContentNiche) -> List[str]:
        """Get relevant keywords for niche"""
        keywords_map = {
            ContentNiche.MOTIVATIONAL: ["motivation", "mindset", "success", "goals", "habits"],
            ContentNiche.AI_TRENDS: ["AI", "ChatGPT", "tech", "innovation", "future"],
            ContentNiche.EDUCATIONAL: ["tutorial", "learn", "skills", "how-to", "guide"],
            ContentNiche.ENTERTAINMENT: ["viral", "trending", "funny", "meme", "entertainment"],
            ContentNiche.TECH_NEWS: ["tech", "news", "update", "breakthrough", "industry"]
        }
        return keywords_map.get(niche, [])


# ============= SCRIPT GENERATION AGENT =============
class ScriptGeneratorExecutor(Executor):
    """
    Generates video scripts with hook, body, and CTA
    """
    
    def __init__(self, id: str = "script_generator"):
        super().__init__(id=id)
    
    @handler
    async def generate_script(self, strategy: dict, ctx: WorkflowContext[ContentScript]) -> None:
        """Generate complete script from strategy"""
        try:
            hook = strategy.get("hook", "Here's something interesting...")
            niche = strategy.get("niche", "general")
            duration_seconds = strategy.get("duration_seconds", 60)
            
            logger.info(f"Generating script for {niche} ({duration_seconds}s)")
            
            # Generate main body
            body_prompt = f"""
            Create engaging, concise video script content (60 seconds) for a {niche} video
            Hook: {hook}
            
            Requirements:
            - Keep it short and punchy (60 seconds when read)
            - Include 2-3 main points
            - Use simple language
            - Build curiosity
            - Include one surprising fact or insight
            - Don't be too salesy
            
            Format:
            [Main Content Body - 40-45 seconds of script]
            """
            
            body = await ai_service.generate_text(body_prompt, max_tokens=200)
            
            # Generate CTA
            cta_prompt = f"""
            Create a natural call-to-action for a {niche} video (5-10 seconds).
            Make it feel organic, not pushy.
            
            Examples:
            - "Drop a comment if you agree"
            - "Subscribe for more content like this"
            - "Share this with someone who needs to see it"
            - "Send this to your group chat"
            
            Generate ONE unique CTA:
            """
            
            cta = await ai_service.generate_text(cta_prompt, max_tokens=50)
            
            script = ContentScript(
                niche=ContentNiche[niche.upper()],
                hook=hook,
                main_body=body or "Default body content",
                call_to_action=cta or "Subscribe for more",
                duration_seconds=duration_seconds,
                tone=strategy.get("tone", "engaging"),
                target_audience=strategy.get("target_audience", "general"),
                keywords=strategy.get("keywords", [])
            )
            
            await ctx.send_message(script)
            
        except Exception as e:
            logger.error(f"Failed to generate script: {e}")


# ============= IMAGE GENERATION AGENT =============
class ImageGeneratorExecutor(Executor):
    """
    Generates images for content using Stable Diffusion
    """
    
    def __init__(self, id: str = "image_generator"):
        super().__init__(id=id)
    
    @handler
    async def generate_images(self, script: ContentScript, ctx: WorkflowContext[list]) -> None:
        """Generate images for script"""
        try:
            logger.info(f"Generating images for: {script.hook[:50]}")
            
            # Create image prompts from script
            image_prompts = self._create_image_prompts(script)
            
            # Generate images
            images = []
            for prompt in image_prompts[:3]:  # Limit to 3 images per script
                image_url = await ai_service.generate_image(prompt, width=1080, height=1920)
                if image_url:
                    images.append({
                        "url": image_url,
                        "prompt": prompt
                    })
            
            logger.info(f"Generated {len(images)} images")
            await ctx.send_message(images)
            
        except Exception as e:
            logger.error(f"Failed to generate images: {e}")
            await ctx.send_message([])
    
    @staticmethod
    def _create_image_prompts(script: ContentScript) -> List[str]:
        """Create visual prompts based on script"""
        prompts = [
            f"Professional eye-catching thumbnail for {script.niche.value} video, high quality, 4K",
            f"Engaging background visual for {script.niche.value} content, modern, trending style",
            f"Attention-grabbing graphic design for {script.niche.value} topic, vibrant colors"
        ]
        return prompts


# ============= AUDIO GENERATION AGENT =============
class AudioGeneratorExecutor(Executor):
    """
    Generates audio/voiceover using TTS
    """
    
    def __init__(self, id: str = "audio_generator"):
        super().__init__(id=id)
    
    @handler
    async def generate_audio(self, script: ContentScript, ctx: WorkflowContext[dict]) -> None:
        """Generate voiceover audio"""
        try:
            logger.info(f"Generating audio for script")
            
            # Combine script parts
            full_script = f"{script.hook} {script.main_body} {script.call_to_action}"
            
            # Generate speech
            audio_url = await ai_service.generate_speech(full_script)
            
            audio = {
                "url": audio_url,
                "text": full_script,
                "duration_seconds": script.duration_seconds
            }
            
            await ctx.send_message(audio)
            
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")


# ============= CONTENT ASSEMBLER AGENT =============
class ContentAssemblerExecutor(Executor):
    """
    Assembles all assets (script, images, audio) into complete content piece
    """
    
    def __init__(self, id: str = "content_assembler"):
        super().__init__(id=id)
    
    @handler
    async def assemble_content(self, inputs: dict, ctx: WorkflowContext[ContentPiece]) -> None:
        """Assemble all components into final content piece"""
        try:
            script = inputs.get("script")
            images = inputs.get("images", [])
            audio = inputs.get("audio", {})
            
            logger.info("Assembling content piece")
            
            content = ContentPiece(
                title=f"{script.niche.value.replace('_', ' ').title()} - {script.hook[:50]}",
                niche=script.niche,
                script=script,
                status="draft",
                created_at=datetime.utcnow()
            )
            
            await ctx.send_message(content)
            
        except Exception as e:
            logger.error(f"Failed to assemble content: {e}")


# ============= BATCH CONTENT GENERATION WORKFLOW =============
async def create_content_generation_workflow() -> WorkflowBuilder:
    """
    Create workflow for batch content generation
    Flow: Strategy → Script → Images → Audio → Assemble
    """
    
    strategy_executor = ContentStrategyExecutor()
    script_executor = ScriptGeneratorExecutor()
    image_executor = ImageGeneratorExecutor()
    audio_executor = AudioGeneratorExecutor()
    assembler_executor = ContentAssemblerExecutor()
    
    return (
        WorkflowBuilder(start_executor=strategy_executor)
        .add_edge(strategy_executor, script_executor)
        .add_edge(script_executor, image_executor)
        .add_edge(script_executor, audio_executor)
        .add_edge(image_executor, assembler_executor)
        .add_edge(audio_executor, assembler_executor)
    )
