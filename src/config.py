"""
Configuration management for Creator-AI
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # System
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Creator-AI"
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    
    # Database
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    # Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "creator-ai-content"
    S3_BUCKET_URL: Optional[str] = None
    
    # AI Models
    OLLAMA_API_URL: str = "http://localhost:11434"
    TEXT_GENERATION_MODEL: str = "mistral:7b"
    TEXT_MODEL_TEMPERATURE: float = 0.7
    TEXT_MODEL_TOP_P: float = 0.9
    
    IMAGE_GENERATION_API: str = "huggingface"
    HUGGINGFACE_API_KEY: Optional[str] = None
    IMAGE_MODEL: str = "stabilityai/stable-diffusion-xl-base-1.0"
    IMAGE_QUALITY: str = "high"
    
    TTS_MODEL: str = "tts_models/en/ljspeech/glow-tts"
    TTS_DEVICE: str = "cpu"
    VOICE_SPEED: float = 1.0
    VOICE_PITCH: float = 1.0
    
    # Video
    FFMPEG_PATH: str = "ffmpeg"
    VIDEO_QUALITY: str = "1080p"
    VIDEO_CODEC: str = "libx264"
    VIDEO_AUDIO_CODEC: str = "aac"
    
    # Platform APIs
    YOUTUBE_API_KEY: Optional[str] = None
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_REFRESH_TOKEN: Optional[str] = None
    YOUTUBE_CHANNEL_ID: Optional[str] = None
    
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None
    META_ACCESS_TOKEN: Optional[str] = None
    META_INSTAGRAM_ACCOUNT_ID: Optional[str] = None
    
    TWITTER_BEARER_TOKEN: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    TWITTER_ACCESS_TOKEN: Optional[str] = None
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = None
    
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    
    # Content Strategy
    CONTENT_NICHES: str = "motivational,ai_trends,educational"
    DEFAULT_NICHE: str = "motivational"
    TARGET_PLATFORMS: str = "youtube_shorts"
    GENERATION_COUNT: int = 1
    POSTING_SCHEDULE: str = "09:00,15:00,21:00"
    BATCH_SIZE: int = 5
    VARIANTS_PER_PIECE: int = 3
    
    # Analytics
    SENTRY_DSN: Optional[str] = None
    ANALYTICS_WRITE_KEY: Optional[str] = None
    PROMETHEUS_ENABLED: bool = False
    PROMETHEUS_PORT: int = 9090
    
    # Scheduling
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "UTC"
    CONTENT_GENERATION_SCHEDULE: str = "cron"
    CONTENT_GENERATION_DAY_OF_WEEK: int = 4  # Friday
    CONTENT_GENERATION_HOUR: int = 20  # 8 PM UTC
    
    # Security
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # Development
    DEBUGPY_ENABLED: bool = False
    DEBUGPY_PORT: int = 5679
    AGENT_DEV_CLI_VERBOSE: bool = False
    USE_MOCK_APIS: bool = False
    
    # Advanced
    WEBHOOK_URL: Optional[str] = None
    CACHE_TTL: int = 3600
    MAX_WORKERS: int = 4
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 5
    
    # Feature Flags
    FEATURE_AUTO_OPTIMIZATION: bool = True
    FEATURE_DUPLICATE_DETECTION: bool = True
    FEATURE_CONTENT_MODERATION: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def niches_list(self) -> List[str]:
        return [n.strip() for n in self.CONTENT_NICHES.split(",")]
    
    @property
    def posting_times_list(self) -> List[str]:
        return [t.strip() for t in self.POSTING_SCHEDULE.split(",")]

    @property
    def target_platforms_list(self) -> List[str]:
        return [p.strip() for p in self.TARGET_PLATFORMS.split(",") if p.strip()]
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


# Create global settings instance
settings = Settings(_env_file=".env" if os.path.exists(".env") else None)
