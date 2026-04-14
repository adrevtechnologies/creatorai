"""
Data models for Creator-AI system
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class ContentNiche(str, Enum):
    """Content niches for generation"""
    MOTIVATIONAL = "motivational"
    AI_TRENDS = "ai_trends"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    TECH_NEWS = "tech_news"


class Platform(str, Enum):
    """Supported platforms"""
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    INSTAGRAM_REELS = "instagram_reels"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


class ContentStatus(str, Enum):
    """Content lifecycle status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class Hook(BaseModel):
    """Content hook/opening formula"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    hook_text: str = Field(..., description="The opening hook formula")
    niche: ContentNiche
    platform: Optional[Platform] = None
    effectiveness_score: float = Field(0.0, ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "hook_text": "You've been doing this wrong your whole life...",
                "niche": "motivational",
                "effectiveness_score": 0.87
            }
        }


class ContentScript(BaseModel):
    """Generated content script"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    niche: ContentNiche
    hook: str
    main_body: str
    call_to_action: str
    duration_seconds: int = 60
    tone: str = "engaging"  # engaging, educational, entertaining
    target_audience: str = "general"
    keywords: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "hook": "You've been doing this wrong...",
                "main_body": "Here's the correct way to do it...",
                "call_to_action": "Subscribe for more tips",
                "duration_seconds": 60
            }
        }


class ContentImage(BaseModel):
    """Generated image/visual asset"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    s3_key: Optional[str] = None
    prompt_used: str
    quality: str  # low, medium, high
    format: str = "png"
    width: int = 1080
    height: int = 1920
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentAudio(BaseModel):
    """Generated audio/voice asset"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    s3_key: Optional[str] = None
    text_used: str
    voice_id: str = "default"
    duration_seconds: float
    quality: str = "high"
    format: str = "mp3"
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentPiece(BaseModel):
    """Complete content piece (multi-modal)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    niche: ContentNiche
    script: ContentScript
    images: List[ContentImage] = []
    audio: Optional[ContentAudio] = None
    video_url: Optional[str] = None
    s3_video_key: Optional[str] = None
    
    status: ContentStatus = ContentStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # Variants for A/B testing
    variants: List[Dict[str, Any]] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "How to Master AI in 60 Seconds",
                "niche": "ai_trends",
                "status": "scheduled"
            }
        }


class DistributionRequest(BaseModel):
    """Request to distribute content"""
    content_id: str
    platforms: List[Platform]
    schedule_datetime: Optional[datetime] = None
    hashtags: List[str] = []
    custom_captions: Dict[Platform, str] = {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "uuid-here",
                "platforms": ["tiktok", "instagram_reels"],
                "hashtags": ["#ai", "#tutorial"]
            }
        }


class DistributionResult(BaseModel):
    """Result of distribution"""
    distribution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    platform: Platform
    external_id: Optional[str] = None
    status: str  # success, failed, pending
    posted_at: Optional[datetime] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "platform": "tiktok",
                "external_id": "7123456789"
            }
        }


class PerformanceMetrics(BaseModel):
    """Performance metrics for content"""
    content_id: str
    platform: Platform
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    watches_percentage: float = 0.0  # avg watch %
    engagement_rate: float = 0.0  # (likes+comments+shares)/views
    reach: int = 0
    impressions: int = 0
    clicks: int = 0
    measured_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def viral_score(self) -> float:
        """Calculate virality score (0-100)"""
        if self.views == 0:
            return 0.0
        return min(100.0, (self.engagement_rate * 1000) + (self.shares * 0.1))


class ContentGenerationRequest(BaseModel):
    """Request to generate content"""
    niche: ContentNiche
    count: int = 1  # How many pieces to generate
    platforms: List[Platform] = []
    custom_hooks: List[str] = []
    variants_per_piece: int = 3
    include_video: bool = True
    include_audio: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "niche": "motivational",
                "count": 5,
                "platforms": ["tiktok", "instagram_reels"],
                "variants_per_piece": 3
            }
        }


class HealthCheckResponse(BaseModel):
    """System health check"""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, bool] = {}  # service_name -> is_operational
    version: str = "1.0.0"
    environment: str = "production"


class AnalyticsReport(BaseModel):
    """Generated analytics report"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    period_start: datetime
    period_end: datetime
    total_content_created: int = 0
    total_content_published: int = 0
    total_views: int = 0
    total_engagement: int = 0
    average_engagement_rate: float = 0.0
    top_performing_content: List[Dict[str, Any]] = []
    top_performing_niche: Optional[ContentNiche] = None
    top_performing_platform: Optional[Platform] = None
    recommendations: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "period_start": "2024-01-01T00:00:00Z",
                "total_content_created": 5,
                "average_engagement_rate": 0.067
            }
        }
