"""
Database service for managing content and metrics
Uses Supabase PostgreSQL with async support
"""
import asyncpg
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger
from src.config import settings
from src.models import ContentPiece, PerformanceMetrics, ContentStatus


class DatabaseService:
    """Manages database operations asynchronously"""
    
    def __init__(self):
        self.pool = None
        self.connection_string = settings.DATABASE_URL or settings.SUPABASE_URL
    
    async def connect(self):
        """Establish connection pool"""
        try:
            if settings.SUPABASE_URL:
                # Format Supabase connection string
                conn_str = f"postgresql://postgres:{settings.SUPABASE_KEY}@db.supabase.co:5432/postgres"
            else:
                conn_str = self.connection_string
            
            self.pool = await asyncpg.create_pool(conn_str, min_size=1, max_size=10)
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def initialize_schema(self):
        """Create required tables if they don't exist"""
        queries = [
            # Content pieces table
            """
            CREATE TABLE IF NOT EXISTS content_pieces (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                niche TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                script JSONB NOT NULL,
                images JSONB DEFAULT '[]'::jsonb,
                audio JSONB,
                video_url TEXT,
                s3_video_key TEXT,
                tags TEXT[] DEFAULT '{}'::text[],
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_for TIMESTAMP,
                published_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            # Performance metrics table
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id SERIAL PRIMARY KEY,
                content_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                views INT DEFAULT 0,
                likes INT DEFAULT 0,
                comments INT DEFAULT 0,
                shares INT DEFAULT 0,
                watches_percentage FLOAT DEFAULT 0,
                engagement_rate FLOAT DEFAULT 0,
                reach INT DEFAULT 0,
                impressions INT DEFAULT 0,
                clicks INT DEFAULT 0,
                measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content_pieces(id) ON DELETE CASCADE
            );
            """,
            # Distribution results table
            """
            CREATE TABLE IF NOT EXISTS distribution_results (
                id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                external_id TEXT,
                status TEXT NOT NULL,
                posted_at TIMESTAMP,
                url TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content_pieces(id) ON DELETE CASCADE
            );
            """,
            # Hooks repository
            """
            CREATE TABLE IF NOT EXISTS content_hooks (
                id TEXT PRIMARY KEY,
                hook_text TEXT NOT NULL,
                niche TEXT NOT NULL,
                platform TEXT,
                effectiveness_score FLOAT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
        
        try:
            async with self.pool.acquire() as conn:
                for query in queries:
                    await conn.execute(query)
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
    
    async def save_content(self, content: ContentPiece) -> bool:
        """Save content piece to database"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO content_pieces (id, title, niche, status, script, tags, metadata, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT(id) DO UPDATE SET
                    status = $4,
                    updated_at = CURRENT_TIMESTAMP
                    """,
                    content.id,
                    content.title,
                    content.niche.value,
                    content.status.value,
                    content.script.dict(),
                    content.tags,
                    content.metadata,
                    content.created_at
                )
            logger.info(f"Content saved: {content.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            return False
    
    async def get_content(self, content_id: str) -> Optional[ContentPiece]:
        """Retrieve content piece"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM content_pieces WHERE id = $1",
                    content_id
                )
                if row:
                    return ContentPiece(**dict(row))
        except Exception as e:
            logger.error(f"Failed to get content: {e}")
        return None
    
    async def save_metrics(self, metrics: PerformanceMetrics) -> bool:
        """Save performance metrics"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO performance_metrics 
                    (content_id, platform, views, likes, comments, shares, 
                     watches_percentage, engagement_rate, reach, impressions, clicks)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    """,
                    metrics.content_id,
                    metrics.platform.value,
                    metrics.views,
                    metrics.likes,
                    metrics.comments,
                    metrics.shares,
                    metrics.watches_percentage,
                    metrics.engagement_rate,
                    metrics.reach,
                    metrics.impressions,
                    metrics.clicks
                )
            logger.info(f"Metrics saved for {metrics.content_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            return False
    
    async def get_content_by_status(self, status: ContentStatus) -> List[ContentPiece]:
        """Get all content with specific status"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM content_pieces WHERE status = $1 ORDER BY created_at DESC",
                    status.value
                )
                return [ContentPiece(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get content by status: {e}")
        return []


# Global database service instance
db_service = DatabaseService()
