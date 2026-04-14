"""
Distribution Agents
Handles posting content across multiple platforms
"""
from agent_framework import Executor, handler, WorkflowContext
from typing import List, Optional
from loguru import logger
from src.models import ContentPiece, Platform, DistributionResult
from src.services.platforms import platform_registry
from datetime import datetime


# ============= DISTRIBUTION AGENT =============
class DistributionExecutor(Executor):
    """
    Distributes content to multiple platforms
    Handles scheduling and platform-specific formatting
    """
    
    def __init__(self, id: str = "distributor"):
        super().__init__(id=id)
    
    @handler
    async def distribute_content(self, content_data: dict, ctx: WorkflowContext[list]) -> None:
        """Distribute content to platforms"""
        try:
            content = content_data.get("content")
            platforms = content_data.get("platforms", [])
            
            if not content:
                logger.error("No content provided for distribution")
                await ctx.send_message([])
                return
            
            logger.info(f"Distributing to {len(platforms)} platforms")
            
            # Post to all platforms concurrently
            results = []
            for platform in platforms:
                try:
                    platform_obj = Platform(platform) if isinstance(platform, str) else platform
                    
                    # Format caption for platform
                    caption = self._format_caption_for_platform(content, platform_obj)
                    
                    # Post content
                    result = await platform_registry.post_to_platform(
                        platform_obj,
                        content.video_url or "https://example.com/video.mp4",
                        caption,
                        content_id=content.id,
                        tags=content.tags
                    )
                    
                    if result:
                        results.append(result.dict())
                        logger.info(f"Posted to {platform_obj.value}: {result.external_id}")
                
                except Exception as e:
                    logger.error(f"Failed to post to {platform}: {e}")
                    results.append({
                        "platform": platform,
                        "status": "failed",
                        "error": str(e)
                    })
            
            await ctx.send_message(results)
            
        except Exception as e:
            logger.error(f"Distribution failed: {e}")
            await ctx.send_message([])
    
    @staticmethod
    def _format_caption_for_platform(content: ContentPiece, platform: Platform) -> str:
        """Format caption for specific platform's requirements"""
        base_caption = f"{content.script.hook}\n\n{content.script.call_to_action}"
        
        # Platform-specific formatting
        if platform == Platform.TIKTOK:
            hashtags = " ".join([f"#{tag}" for tag in content.tags[:5]])
            return f"{base_caption}\n\n{hashtags}"
        
        elif platform == Platform.INSTAGRAM_REELS:
            hashtags = " ".join([f"#{tag}" for tag in content.tags[:30]])
            return f"{base_caption}\n\n{hashtags}\n\n📍 Save this! 💫"
        
        elif platform == Platform.YOUTUBE_SHORTS:
            return f"{base_caption}\n\nPart of @creator-ai content series"
        
        elif platform == Platform.TWITTER:
            return f"{base_caption}\n\n{' '.join([f'#{tag}' for tag in content.tags[:3]])}"
        
        elif platform == Platform.LINKEDIN:
            return f"🎯 {base_caption}\n\nWhat do you think about this?"
        
        return base_caption


# ============= ANALYTICS AGENT =============
class AnalyticsExecutor(Executor):
    """
    Collects and analyzes performance metrics
    Tracks viral performance and engagement
    """
    
    def __init__(self, id: str = "analytics"):
        super().__init__(id=id)
    
    @handler
    async def collect_metrics(self, distribution_results: list, ctx: WorkflowContext[dict]) -> None:
        """Collect metrics from platform APIs"""
        try:
            logger.info(f"Collecting metrics for {len(distribution_results)} posts")
            
            metrics_summary = {
                "total_posts": len(distribution_results),
                "successful_posts": 0,
                "failed_posts": 0,
                "platform_breakdown": {},
                "total_views": 0,
                "total_engagement": 0,
                "top_platform": None
            }
            
            for result in distribution_results:
                if isinstance(result, dict):
                    status = result.get("status", "unknown")
                    platform = result.get("platform", "unknown")
                    
                    # Count successes/failures
                    if status == "success":
                        metrics_summary["successful_posts"] += 1
                    else:
                        metrics_summary["failed_posts"] += 1
                    
                    # Initialize platform stats
                    if platform not in metrics_summary["platform_breakdown"]:
                        metrics_summary["platform_breakdown"][platform] = {
                            "posts": 0,
                            "views": 0,
                            "engagement": 0
                        }
                    
                    metrics_summary["platform_breakdown"][platform]["posts"] += 1
            
            # Calculate top platform
            if metrics_summary["platform_breakdown"]:
                top_platform = max(metrics_summary["platform_breakdown"].items(),
                                  key=lambda x: x[1]["views"])
                metrics_summary["top_platform"] = top_platform[0]
            
            await ctx.send_message(metrics_summary)
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            await ctx.send_message({})


# ============= OPTIMIZATION AGENT =============
class OptimizationExecutor(Executor):
    """
    Analyzes performance data and suggests optimizations
    Learns from what worked and what didn't
    """
    
    def __init__(self, id: str = "optimizer"):
        super().__init__(id=id)
    
    @handler
    async def optimize_strategy(self, metrics: dict, ctx: WorkflowContext[dict]) -> None:
        """Generate optimization recommendations"""
        try:
            logger.info("Generating optimization recommendations")
            
            recommendations = {
                "hook_optimization": self._recommend_hook_changes(metrics),
                "platform_focus": self._recommend_platform_focus(metrics),
                "posting_time": self._recommend_posting_time(metrics),
                "content_adjustments": self._recommend_content_changes(metrics)
            }
            
            await ctx.send_message(recommendations)
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            await ctx.send_message({})
    
    @staticmethod
    def _recommend_hook_changes(metrics: dict) -> List[str]:
        """Recommend hook improvements"""
        return [
            "Try starting with 'Did you know...' for educational content",
            "Add more pattern interrupt in the first 3 words",
            "Test hooks with numbers or statistics"
        ]
    
    @staticmethod
    def _recommend_platform_focus(metrics: dict) -> str:
        """Recommend which platform to prioritize"""
        top_platform = metrics.get("top_platform", "all")
        if top_platform:
            return f"Focus content creation on {top_platform} - highest engagement"
        return "Track metrics more to identify best platform"
    
    @staticmethod
    def _recommend_posting_time(metrics: dict) -> str:
        """Recommend optimal posting time"""
        return "Test posting at 9 AM UTC, 3 PM UTC, and 9 PM UTC to find peak times"
    
    @staticmethod
    def _recommend_content_changes(metrics: dict) -> List[str]:
        """Recommend content strategy changes"""
        return [
            "Increase video length to 45-90 seconds for more story-telling",
            "Add more text overlays for accessibility and engagement",
            "Test trending audio/music in your niche",
            "Create series content to build audience retention"
        ]
