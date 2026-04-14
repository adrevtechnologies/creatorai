"""
Creator-AI Main Entry Point
Supports both CLI and HTTP server modes
"""
import asyncio
import sys
import argparse
from loguru import logger
from src.config import settings
from src.services.database import db_service
from datetime import datetime


# Configure logging
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL, format="<level>{time:HH:mm:ss}</level> | <level>{level: <8}</level> | <level>{message}</level>")
logger.add(f"logs/creator-ai-{datetime.now().strftime('%Y%m%d')}.log", level="DEBUG", rotation="500 MB")


async def startup():
    """Initialize services"""
    try:
        logger.info("Initializing Creator-AI services...")
        
        # Initialize database
        await db_service.connect()
        await db_service.initialize_schema()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


async def shutdown():
    """Cleanup resources"""
    try:
        logger.info("Shutting down services...")
        await db_service.disconnect()
        logger.info("✅ Shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


async def main_cli():
    """Run in CLI mode - interactive commands"""
    from src.workflows.orchestrator import create_orchestrator_workflow
    
    logger.info("🎬 Creator-AI CLI Mode")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    try:
        # Create workflow
        workflow_builder = await create_orchestrator_workflow()
        workflow = workflow_builder.build()
        
        # Example: Generate content for motivational niche
        request = {
            "niche": "motivational",
            "count": 1,
            "platforms": ["tiktok", "instagram_reels"]
        }
        
        logger.info(f"Processing request: {request}")
        
        # Run workflow
        result = await workflow.run(request, stream=True)
        
        logger.info(f"✅ Workflow completed: {result}")
        
    except Exception as e:
        logger.error(f"❌ CLI Error: {e}", exc_info=True)
        sys.exit(1)


async def main_server():
    """Run as HTTP server using agent-server"""
    try:
        from azure.ai.agentserver.agentframework import from_agent_framework
        from src.workflows.orchestrator import create_orchestrator_agent
        
        logger.info("🚀 Creator-AI HTTP Server Mode")
        logger.info(f"Listening on {settings.APP_HOST}:{settings.APP_PORT}")
        
        # Create agent
        agent = await create_orchestrator_agent()
        
        # Start server
        await from_agent_framework(agent).run_async()
        
    except ImportError:
        logger.error("❌ azure-ai-agentserver packages not installed. Install with:")
        logger.error("   pip install azure-ai-agentserver-core==1.0.0b16 azure-ai-agentserver-agentframework==1.0.0b16")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Server Error: {e}", exc_info=True)
        sys.exit(1)


async def main_scheduler():
    """Run scheduled content generation"""
    from src.workflows.orchestrator import create_orchestrator_workflow
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    
    logger.info("📅 Creator-AI Scheduler Mode")
    logger.info(f"Schedule: {settings.CONTENT_GENERATION_DAY_OF_WEEK} at {settings.CONTENT_GENERATION_HOUR}:00 UTC")
    
    try:
        scheduler = AsyncIOScheduler()
        
        # Schedule content generation
        async def generate_content():
            logger.info("⏰ Scheduled content generation starting...")
            try:
                workflow_builder = await create_orchestrator_workflow()
                workflow = workflow_builder.build()
                
                request = {
                    "niche": "motivational",
                    "count": settings.BATCH_SIZE,
                    "platforms": ["tiktok", "instagram_reels", "youtube_shorts"]
                }
                
                result = await workflow.run(request, stream=True)
                logger.info(f"✅ Scheduled generation completed: {result}")
            except Exception as e:
                logger.error(f"❌ Planned generation failed: {e}", exc_info=True)
        
        # Add scheduled job (day_of_week: 4 = Friday)
        scheduler.add_job(
            generate_content,
            'cron',
            day_of_week=settings.CONTENT_GENERATION_DAY_OF_WEEK,
            hour=settings.CONTENT_GENERATION_HOUR,
            timezone=settings.SCHEDULER_TIMEZONE,
            id='weekly_content_generation'
        )
        
        scheduler.start()
        logger.info("✅ Scheduler started")
        
        # Keep scheduler running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"❌ Scheduler Error: {e}", exc_info=True)
        sys.exit(1)


async def health_check():
    """Check system health"""
    logger.info("🏥 Health Check Mode")
    
    try:
        checks = {
            "database": await db_service.pool is not None if db_service else False,
            "config_loaded": settings is not None,
            "ai_service_ready": True,
            "storage_configured": settings.AWS_ACCESS_KEY_ID is not None,
        }
        
        logger.info("Health Check Results:")
        for service, status in checks.items():
            symbol = "✅" if status else "❌"
            logger.info(f"  {symbol} {service}: {status}")
        
        all_healthy = all(checks.values())
        if all_healthy:
            logger.info("✅ All systems operational")
            sys.exit(0)
        else:
            logger.warning("⚠️  Some services not ready")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Creator-AI Content Automation System")
    parser.add_argument(
        "mode",
        nargs="?",
        default="server",
        choices=["cli", "server", "scheduler", "health"],
        help="Execution mode"
    )
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--server", action="store_true", help="Run as HTTP server")
    parser.add_argument("--scheduler", action="store_true", help="Run scheduler")
    parser.add_argument("--health", action="store_true", help="Run health check")
    
    args = parser.parse_args()
    
    # Determine mode
    mode = args.mode
    if args.cli:
        mode = "cli"
    elif args.server:
        mode = "server"
    elif args.scheduler:
        mode = "scheduler"
    elif args.health:
        mode = "health"
    
    logger.info(f"Creator-AI v{__import__('src', fromlist=['__version__']).__version__}")
    logger.info("=" * 60)
    
    try:
        # Setup
        asyncio.run(startup())
        
        # Run mode
        if mode == "cli":
            asyncio.run(main_cli())
        elif mode == "server":
            asyncio.run(main_server())
        elif mode == "scheduler":
            asyncio.run(main_scheduler())
        elif mode == "health":
            asyncio.run(health_check())
        
    except KeyboardInterrupt:
        logger.info("\n⏸️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        try:
            asyncio.run(shutdown())
        except:
            pass
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
