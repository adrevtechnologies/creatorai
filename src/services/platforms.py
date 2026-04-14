"""
Platform integration services
Handles posting and analytics across all supported platforms
"""
import httpx
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from src.config import settings
from src.models import Platform, DistributionResult
from datetime import datetime


class PlatformService:
    """Base class for platform integrations"""
    
    async def post_content(self, video_url: str, caption: str, 
                          tags: list = None, **kwargs) -> Optional[DistributionResult]:
        """Post content to platform"""
        raise NotImplementedError
    
    async def get_metrics(self, external_id: str) -> Dict[str, Any]:
        """Retrieve metrics for posted content"""
        raise NotImplementedError


class YouTubeShortsService(PlatformService):
    """YouTube Shorts integration"""
    
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.channel_id = settings.YOUTUBE_CHANNEL_ID
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def post_content(self, video_url: str, caption: str, 
                          tags: list = None, **kwargs) -> Optional[DistributionResult]:
        """Upload Short to YouTube"""
        try:
            logger.info(f"Uploading to YouTube Shorts: {caption[:50]}")
            
            # This would use YouTube Data API v3 to upload video
            # Requires OAuth2 authentication flow
            
            # Mock implementation
            external_id = f"youtube_{datetime.utcnow().timestamp()}"
            
            result = DistributionResult(
                content_id=kwargs.get("content_id", ""),
                platform=Platform.YOUTUBE_SHORTS,
                external_id=external_id,
                status="success" if settings.USE_MOCK_APIS else "pending",
                posted_at=datetime.utcnow(),
                url=f"https://youtube.com/shorts/{external_id}"
            )
            
            logger.info(f"YouTube upload successful: {external_id}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to upload to YouTube: {e}")
            return None
    
    async def get_metrics(self, external_id: str) -> Dict[str, Any]:
        """Get YouTube Shorts metrics"""
        try:
            # Would call YouTube Data API
            return {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        except Exception as e:
            logger.error(f"Failed to get YouTube metrics: {e}")
            return {}


class TikTokService(PlatformService):
    """TikTok integration"""
    
    def __init__(self):
        self.client_key = settings.TIKTOK_CLIENT_KEY
        self.client_secret = settings.TIKTOK_CLIENT_SECRET
        self.access_token = settings.TIKTOK_ACCESS_TOKEN
        self.base_url = "https://open.tiktokapis.com/v1"
    
    async def post_content(self, video_url: str, caption: str, 
                          tags: list = None, **kwargs) -> Optional[DistributionResult]:
        """Upload video to TikTok"""
        try:
            logger.info(f"Uploading to TikTok: {caption[:50]}")
            
            # This would use TikTok Creator API
            # Requires OAuth2 authentication
            
            # Mock implementation
            external_id = f"tiktok_{datetime.utcnow().timestamp()}"
            
            result = DistributionResult(
                content_id=kwargs.get("content_id", ""),
                platform=Platform.TIKTOK,
                external_id=external_id,
                status="success" if settings.USE_MOCK_APIS else "pending",
                posted_at=datetime.utcnow(),
                url=f"https://tiktok.com/@user/video/{external_id}"
            )
            
            logger.info(f"TikTok upload successful: {external_id}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to upload to TikTok: {e}")
            return None
    
    async def get_metrics(self, external_id: str) -> Dict[str, Any]:
        """Get TikTok video metrics"""
        try:
            # Would call TikTok API
            return {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        except Exception as e:
            logger.error(f"Failed to get TikTok metrics: {e}")
            return {}


class InstagramReelsService(PlatformService):
    """Instagram Reels integration via Meta Graph API"""
    
    def __init__(self):
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET
        self.access_token = settings.META_ACCESS_TOKEN
        self.account_id = settings.META_INSTAGRAM_ACCOUNT_ID
        self.base_url = "https://graph.instagram.com"
    
    async def post_content(self, video_url: str, caption: str, 
                          tags: list = None, **kwargs) -> Optional[DistributionResult]:
        """Upload Reel to Instagram"""
        try:
            logger.info(f"Uploading to Instagram Reels: {caption[:50]}")
            
            # This would use Meta Graph API
            # Requires page access token
            
            # Mock implementation
            external_id = f"ig_{datetime.utcnow().timestamp()}"
            
            result = DistributionResult(
                content_id=kwargs.get("content_id", ""),
                platform=Platform.INSTAGRAM_REELS,
                external_id=external_id,
                status="success" if settings.USE_MOCK_APIS else "pending",
                posted_at=datetime.utcnow(),
                url=f"https://instagram.com/reel/{external_id}"
            )
            
            logger.info(f"Instagram upload successful: {external_id}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to upload to Instagram: {e}")
            return None
    
    async def get_metrics(self, external_id: str) -> Dict[str, Any]:
        """Get Instagram Reels metrics"""
        try:
            # Would call Meta API
            return {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        except Exception as e:
            logger.error(f"Failed to get Instagram metrics: {e}")
            return {}


class TwitterService(PlatformService):
    """Twitter/X integration"""
    
    def __init__(self):
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        self.base_url = "https://api.twitter.com/2"
    
    async def post_content(self, video_url: str, caption: str, 
                          tags: list = None, **kwargs) -> Optional[DistributionResult]:
        """Post video to Twitter/X"""
        try:
            logger.info(f"Posting to Twitter: {caption[:50]}")
            
            # This would use Twitter API v2
            # Upload media first, then create tweet
            
            # Mock implementation
            external_id = f"tweet_{datetime.utcnow().timestamp()}"
            
            result = DistributionResult(
                content_id=kwargs.get("content_id", ""),
                platform=Platform.TWITTER,
                external_id=external_id,
                status="success" if settings.USE_MOCK_APIS else "pending",
                posted_at=datetime.utcnow(),
                url=f"https://twitter.com/user/status/{external_id}"
            )
            
            logger.info(f"Twitter post successful: {external_id}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to post to Twitter: {e}")
            return None
    
    async def get_metrics(self, external_id: str) -> Dict[str, Any]:
        """Get tweet metrics"""
        try:
            # Would call Twitter API
            return {
                "views": 0,
                "likes": 0,
                "retweets": 0,
                "replies": 0
            }
        except Exception as e:
            logger.error(f"Failed to get Twitter metrics: {e}")
            return {}


class LinkedInService(PlatformService):
    """LinkedIn integration"""
    
    def __init__(self):
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.base_url = "https://api.linkedin.com/v2"
    
    async def post_content(self, video_url: str, caption: str, 
                          tags: list = None, **kwargs) -> Optional[DistributionResult]:
        """Post content to LinkedIn"""
        try:
            logger.info(f"Posting to LinkedIn: {caption[:50]}")
            
            # Mock implementation
            external_id = f"linkedin_{datetime.utcnow().timestamp()}"
            
            result = DistributionResult(
                content_id=kwargs.get("content_id", ""),
                platform=Platform.LINKEDIN,
                external_id=external_id,
                status="success" if settings.USE_MOCK_APIS else "pending",
                posted_at=datetime.utcnow(),
                url=f"https://linkedin.com/feed/update/{external_id}"
            )
            
            logger.info(f"LinkedIn post successful: {external_id}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {e}")
            return None
    
    async def get_metrics(self, external_id: str) -> Dict[str, Any]:
        """Get LinkedIn post metrics"""
        try:
            return {
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        except Exception as e:
            logger.error(f"Failed to get LinkedIn metrics: {e}")
            return {}


class PlatformServiceRegistry:
    """Registry of all platform services"""
    
    services = {
        Platform.YOUTUBE_SHORTS: YouTubeShortsService(),
        Platform.TIKTOK: TikTokService(),
        Platform.INSTAGRAM_REELS: InstagramReelsService(),
        Platform.TWITTER: TwitterService(),
        Platform.LINKEDIN: LinkedInService(),
    }
    
    @classmethod
    def get_service(cls, platform: Platform) -> Optional[PlatformService]:
        """Get service for platform"""
        return cls.services.get(platform)
    
    @classmethod
    async def post_to_platform(cls, platform: Platform, video_url: str, 
                               caption: str, **kwargs) -> Optional[DistributionResult]:
        """Post content to specific platform"""
        service = cls.get_service(platform)
        if service:
            return await service.post_content(video_url, caption, **kwargs)
        logger.error(f"No service found for platform: {platform}")
        return None
    
    @classmethod
    async def post_to_all(cls, platforms: list, video_url: str, 
                          caption: str, **kwargs) -> list:
        """Post to multiple platforms concurrently"""
        tasks = [
            cls.post_to_platform(platform, video_url, caption, **kwargs)
            for platform in platforms
        ]
        return await asyncio.gather(*tasks)


# Global platform registry
platform_registry = PlatformServiceRegistry()
