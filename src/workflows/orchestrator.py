"""
Main Orchestrator Workflow
Coordinates all agents in a complete content generation and distribution pipeline
"""
from agent_framework import (
    WorkflowBuilder,
    Executor,
    handler,
    WorkflowContext,
    Message,
    AgentResponseUpdate,
    Content
)
from typing import List
from loguru import logger
from datetime import datetime
from src.models import ContentNiche, Platform, ContentStatus
from src.config import settings
from src.agents.content_generator import (
    ContentStrategyExecutor,
    ScriptGeneratorExecutor,
    ImageGeneratorExecutor,
    AudioGeneratorExecutor,
    ContentAssemblerExecutor
)
from src.agents.distribution import DistributionExecutor, AnalyticsExecutor, OptimizationExecutor
from src.services.database import db_service


# ============= ORCHESTRATOR EXECUTOR =============
class OrchestratorExecutor(Executor):
    """
    Main orchestrator that coordinates entire workflow
    Entry point for content generation requests
    """
    
    def __init__(self, id: str = "orchestrator"):
        super().__init__(id=id)
    
    @handler
    async def orchestrate(
        self,
        messages: List[Message],
        ctx: WorkflowContext[dict]
    ) -> None:
        """
        Main orchestration handler
        Accepts user requests and coordinates workflow
        """
        try:
            # Parse user input
            user_input = messages[-1].content if messages else {}
            
            if isinstance(user_input, str):
                # Handle string input (CLI mode)
                request_data = {"niche": "motivational", "count": 1}
            else:
                request_data = user_input
            
            logger.info(f"Orchestrator received: {request_data}")
            
            niche = request_data.get("niche", ContentNiche.MOTIVATIONAL.value)
            count = request_data.get("count", 1)
            platforms = request_data.get("platforms", settings.target_platforms_list or [Platform.YOUTUBE_SHORTS.value])
            
            # Send response update
            await ctx.yield_output(
                AgentResponseUpdate(
                    contents=[Content("text", text=f"Starting content generation pipeline for {niche}")],
                    role="assistant",
                    author_name=self.id
                )
            )
            
            # Forward to next executor with parsed data
            await ctx.send_message({
                "niche": niche,
                "count": count,
                "platforms": platforms
            })
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            await ctx.yield_output(
                AgentResponseUpdate(
                    contents=[Content("text", text=f"Error: {str(e)}")],
                    role="assistant",
                    author_name=self.id
                )
            )


# ============= BATCH PROCESSOR EXECUTOR =============
class BatchProcessorExecutor(Executor):
    """
    Processes batches of content generation requests
    Creates multiple content pieces in sequence
    """
    
    def __init__(self, id: str = "batch_processor"):
        super().__init__(id=id)
    
    @handler
    async def process_batch(self, request: dict, ctx: WorkflowContext[list]) -> None:
        """Process batch of content"""
        try:
            niche = ContentNiche[request.get("niche", "MOTIVATIONAL").upper()]
            count = request.get("count", 1)
            platforms = [Platform(p) if isinstance(p, str) else p for p in request.get("platforms", [])]
            
            logger.info(f"Processing batch: {count} pieces for {niche.value}")
            
            content_batch = []
            for i in range(count):
                content_request = {
                    "niche": niche,
                    "item_number": i + 1,
                    "total_items": count,
                    "platforms": platforms
                }
                content_batch.append(content_request)
            
            await ctx.send_message(content_batch)
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            await ctx.send_message([])


# ============= RESULTS AGGREGATOR EXECUTOR =============
class ResultsAggregatorExecutor(Executor):
    """
    Aggregates results from entire pipeline
    Prepares final output
    """
    
    def __init__(self, id: str = "results_aggregator"):
        super().__init__(id=id)
    
    @handler
    async def aggregate_results(
        self,
        workflow_data: dict,
        ctx: WorkflowContext[dict]
    ) -> None:
        """Aggregate final results"""
        try:
            logger.info("Aggregating workflow results")
            
            result = {
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat(),
                "content_created": workflow_data.get("content_count", 0),
                "content_published": workflow_data.get("published_count", 0),
                "distribution_results": workflow_data.get("distribution_results", []),
                "performance_metrics": workflow_data.get("metrics", {}),
                "recommendations": workflow_data.get("recommendations", {})
            }
            
            await ctx.send_message(result)
            
        except Exception as e:
            logger.error(f"Result aggregation failed: {e}")


# ============= WORKFLOW BUILDER =============
async def create_orchestrator_workflow() -> WorkflowBuilder:
    """
    Create complete orchestrator workflow
    
    Pipeline:
    1. Orchestrator - Parse request
    2. BatchProcessor - Create content batch
    3. ContentStrategy - Generate strategy
    4. ScriptGenerator - Generate script
    5. ImageGenerator & AudioGenerator - Generate assets (parallel)
    6. ContentAssembler - Assemble final piece
    7. Distributor - Post to platforms
    8. Analytics - Collect metrics
    9. Optimizer - Generate recommendations
    10. ResultsAggregator - Finalize output
    """
    
    # Initialize all executors
    orchestrator = OrchestratorExecutor()
    batch_processor = BatchProcessorExecutor()
    strategy = ContentStrategyExecutor()
    script_gen = ScriptGeneratorExecutor()
    image_gen = ImageGeneratorExecutor()
    audio_gen = AudioGeneratorExecutor()
    assembler = ContentAssemblerExecutor()
    distributor = DistributionExecutor()
    analytics = AnalyticsExecutor()
    optimizer = OptimizationExecutor()
    aggregator = ResultsAggregatorExecutor()
    
    # Build workflow graph
    workflow = (
        WorkflowBuilder(start_executor=orchestrator)
        .add_edge(orchestrator, batch_processor)
        .add_edge(batch_processor, strategy)
        .add_edge(strategy, script_gen)
        .add_edge(script_gen, image_gen)
        .add_edge(script_gen, audio_gen)
        .add_edge(image_gen, assembler)
        .add_edge(audio_gen, assembler)
        .add_edge(assembler, distributor)
        .add_edge(distributor, analytics)
        .add_edge(analytics, optimizer)
        .add_edge(optimizer, aggregator)
    )
    
    return workflow


# ============= WORKFLOW AS AGENT =============
async def create_orchestrator_agent():
    """
    Build orchestrator as an agent for HTTP server hosting
    This allows serving as REST API with the agent-server package
    """
    workflow = await create_orchestrator_workflow()
    agent = workflow.build().as_agent()
    return agent
