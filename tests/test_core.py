"""Test suite for Creator-AI"""

import pytest
from unittest.mock import patch, MagicMock
from src.config import settings
from src.models import ContentNiche, Platform, ContentStatus


class TestConfig:
    """Test configuration loading"""
    
    def test_settings_loaded(self):
        """Verify settings are loaded"""
        assert settings is not None
        assert settings.ENVIRONMENT in ["development", "production", "staging"]
    
    def test_niches_list(self):
        """Test niche parsing"""
        niches = settings.niches_list
        assert len(niches) > 0
        assert all(isinstance(n, str) for n in niches)
    
    def test_is_production(self):
        """Test production detection"""
        result = settings.is_production()
        assert isinstance(result, bool)


class TestModels:
    """Test data models"""
    
    def test_content_niche_enum(self):
        """Test niche enum"""
        assert ContentNiche.MOTIVATIONAL.value == "motivational"
        assert ContentNiche.AI_TRENDS.value == "ai_trends"
    
    def test_platform_enum(self):
        """Test platform enum"""
        assert Platform.TIKTOK.value == "tiktok"
        assert Platform.YOUTUBE_SHORTS.value == "youtube_shorts"
    
    def test_content_status_enum(self):
        """Test status enum"""
        assert ContentStatus.DRAFT.value == "draft"
        assert ContentStatus.PUBLISHED.value == "published"


@pytest.mark.asyncio
async def test_async_operations():
    """Test async functionality can be called"""
    # Placeholder for async tests
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
