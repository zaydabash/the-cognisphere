"""
FastAPI application for The Cognisphere simulation engine.

Provides REST API endpoints for controlling simulations, accessing data,
and real-time visualization of emergent civilization dynamics.
"""

import asyncio
import os
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator
import uvicorn

from simulation.engine import SimulationEngine, SimulationConfig, SimulationState
from simulation.environmental_stimuli import StimulusType
from adapters import LLMMode


# Security
security = HTTPBearer(auto_error=False)

# Environment-based configuration
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:5174"
).split(",")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Request/Response models with validation
class SimulationConfigRequest(BaseModel):
    num_agents: int = Field(default=300, ge=1, le=10000, description="Number of agents")
    seed: Optional[int] = Field(default=42, ge=0, description="Random seed")
    max_ticks: int = Field(default=10000, ge=1, le=1000000, description="Maximum simulation ticks")
    llm_mode: str = Field(default="mock", description="LLM mode")
    llm_model: str = Field(default="gpt-3.5-turbo", max_length=100, description="LLM model name")
    llm_temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="LLM temperature")
    tick_duration_ms: int = Field(default=100, ge=1, le=10000, description="Tick duration in ms")
    agents_per_tick: int = Field(default=50, ge=1, le=1000, description="Agents processed per tick")
    interactions_per_tick: int = Field(default=100, ge=1, le=10000, description="Interactions per tick")
    memory_backend: str = Field(default="networkx", description="Memory backend")
    vector_backend: str = Field(default="faiss", description="Vector backend")
    snapshot_frequency: int = Field(default=20, ge=1, le=1000, description="Snapshot frequency")
    snapshot_directory: str = Field(default="snapshots", max_length=200, description="Snapshot directory")
    stimuli_file: Optional[str] = Field(default=None, max_length=500, description="Stimuli file path")
    
    @field_validator("snapshot_directory")
    @classmethod
    def validate_snapshot_directory(cls, v):
        """Validate snapshot directory doesn't contain path traversal."""
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid snapshot directory path")
        return v
    
    @field_validator("stimuli_file")
    @classmethod
    def validate_stimuli_file(cls, v):
        """Validate stimuli file path doesn't contain path traversal."""
        if v and (".." in v or v.startswith("/")):
            raise ValueError("Invalid stimuli file path")
        return v


class SimulationControlRequest(BaseModel):
    action: str = Field(..., description="Action to perform")
    
    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        """Validate action is one of the allowed values."""
        allowed_actions = ["start", "pause", "resume", "stop", "step"]
        if v.lower() not in allowed_actions:
            raise ValueError(f"Action must be one of: {', '.join(allowed_actions)}")
        return v.lower()


class SnapshotRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100, description="Snapshot name")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate snapshot name doesn't contain dangerous characters."""
        if v and (".." in v or "/" in v or "\\" in v):
            raise ValueError("Invalid snapshot name")
        return v


# Global simulation engine instance
simulation_engine: Optional[SimulationEngine] = None

# Create FastAPI app
app = FastAPI(
    title="The Cognisphere API",
    description="API for emergent intelligence civilization simulation",
    version="0.1.0"
)

# Add CORS middleware with environment-based configuration
# In production, restrict to allowed origins; in development, allow all
cors_origins = ALLOWED_ORIGINS if ENVIRONMENT == "production" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the simulation engine on startup."""
    global simulation_engine
    try:
        config = SimulationConfig()
        simulation_engine = SimulationEngine(config)
        print("Simulation engine initialized on startup")
    except Exception as e:
        print(f"Failed to initialize simulation engine: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global simulation_engine
    if simulation_engine:
        simulation_engine.cleanup()
        print("Simulation engine cleaned up")


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/healthz")
async def healthz():
    """Kubernetes-style health check endpoint."""
    return {"ok": True}

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "name": "The Cognisphere API",
        "version": "0.1.0",
        "description": "Emergent Intelligence Civilization Engine API",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "healthz": "/healthz",
            "simulation": "/simulation",
            "agents": "/agents",
            "culture": "/culture",
            "economy": "/economy"
        }
    }


# Simulation control endpoints
@app.post("/simulation/initialize")
async def initialize_simulation(config: SimulationConfigRequest):
    """
    Initialize a new simulation with the given configuration.
    
    Validates input and creates a new simulation engine instance.
    """
    global simulation_engine
    
    try:
        # Validate LLM mode
        try:
            llm_mode = LLMMode(config.llm_mode)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid LLM mode: {config.llm_mode}"
            )
        
        # Convert request to config
        sim_config = SimulationConfig(
            num_agents=config.num_agents,
            seed=config.seed,
            max_ticks=config.max_ticks,
            llm_mode=llm_mode,
            llm_model=config.llm_model,
            llm_temperature=config.llm_temperature,
            tick_duration_ms=config.tick_duration_ms,
            agents_per_tick=config.agents_per_tick,
            interactions_per_tick=config.interactions_per_tick,
            memory_backend=config.memory_backend,
            vector_backend=config.vector_backend,
            snapshot_frequency=config.snapshot_frequency,
            snapshot_directory=config.snapshot_directory,
            stimuli_file=config.stimuli_file
        )
        
        # Create new simulation engine
        simulation_engine = SimulationEngine(sim_config)
        success = await simulation_engine.initialize()
        
        if success:
            return {"status": "initialized", "config": sim_config.to_dict()}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize simulation"
            )
            
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Don't leak internal error details in production
        error_detail = str(e) if ENVIRONMENT != "production" else "Internal server error"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@app.post("/simulation/control")
async def control_simulation(request: SimulationControlRequest):
    """Control simulation execution (start, pause, resume, stop, step)."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        action = request.action.lower()
        
        if action == "start":
            if simulation_engine.state == SimulationState.READY:
                # Start simulation in background
                asyncio.create_task(simulation_engine.run_simulation())
                return {"status": "started"}
            else:
                raise HTTPException(status_code=400, detail="Simulation not ready")
        
        elif action == "pause":
            await simulation_engine.pause_simulation()
            return {"status": "paused"}
        
        elif action == "resume":
            await simulation_engine.resume_simulation()
            return {"status": "resumed"}
        
        elif action == "stop":
            await simulation_engine.stop_simulation()
            return {"status": "stopped"}
        
        elif action == "step":
            await simulation_engine.step_simulation()
            return {"status": "stepped"}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/simulation/status")
async def get_simulation_status():
    """Get current simulation status."""
    global simulation_engine
    
    if not simulation_engine:
        return {"status": "not_initialized"}
    
    try:
        status = await simulation_engine.get_simulation_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Data access endpoints
@app.get("/agents")
async def get_agents(agent_id: Optional[str] = None):
    """Get agent data."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        data = await simulation_engine.get_agent_data(agent_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent data."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        data = await simulation_engine.get_agent_data(agent_id)
        if not data:
            raise HTTPException(status_code=404, detail="Agent not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/culture")
async def get_cultural_data():
    """Get cultural data (myths, norms, slang)."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        data = await simulation_engine.get_cultural_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/economy")
async def get_economic_data():
    """Get economic data."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        data = await simulation_engine.get_economic_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/network")
async def get_network_data():
    """Get agent network data for visualization."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        data = await simulation_engine.get_network_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/world")
async def get_world_summary():
    """Get comprehensive world summary."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        if simulation_engine.world:
            summary = simulation_engine.world.get_world_summary()
            return summary
        else:
            return {"error": "World not initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Snapshot endpoints
@app.post("/snapshots")
async def take_snapshot(request: SnapshotRequest):
    """Take a snapshot of the current simulation state."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        snapshot_file = await simulation_engine.take_snapshot(request.name)
        return {"status": "snapshot_created", "file": snapshot_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/snapshots")
async def list_snapshots():
    """List available snapshots."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        snapshots = simulation_engine.snapshots
        return {"snapshots": [{"name": s["name"], "tick": s["tick"], "timestamp": s["timestamp"]} for s in snapshots]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/snapshots/load")
async def load_snapshot(snapshot_file: str):
    """Load a snapshot and restore simulation state."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        success = await simulation_engine.load_snapshot(snapshot_file)
        if success:
            return {"status": "snapshot_loaded", "file": snapshot_file}
        else:
            raise HTTPException(status_code=500, detail="Failed to load snapshot")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Real-time data endpoints for dashboard
@app.get("/realtime/status")
async def get_realtime_status():
    """Get real-time simulation status for dashboard."""
    global simulation_engine
    
    if not simulation_engine:
        return {"status": "not_initialized", "data": None}
    
    try:
        status = await simulation_engine.get_simulation_status()
        
        # Add real-time metrics
        if simulation_engine.world:
            status["realtime"] = {
                "current_tick": simulation_engine.world.current_tick,
                "agent_count": len(simulation_engine.world.agents),
                "faction_count": len(simulation_engine.world.factions),
                "active_events": len(simulation_engine.world.event_system.active_events),
                "myth_count": len(simulation_engine.world.culture.myths),
                "norm_count": len(simulation_engine.world.culture.active_norms),
                "trade_count": len(simulation_engine.world.economy.trade_history)
            }
        
        return status
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/realtime/network")
async def get_realtime_network():
    """Get real-time network data for visualization."""
    global simulation_engine
    
    if not simulation_engine:
        return {"nodes": [], "edges": []}
    
    try:
        data = await simulation_engine.get_network_data()
        return data
    except Exception as e:
        return {"nodes": [], "edges": [], "error": str(e)}


@app.get("/realtime/culture")
async def get_realtime_culture():
    """Get real-time cultural data."""
    global simulation_engine
    
    if not simulation_engine:
        return {"myths": [], "norms": [], "slang": []}
    
    try:
        data = await simulation_engine.get_cultural_data()
        return data
    except Exception as e:
        return {"myths": [], "norms": [], "slang": [], "error": str(e)}


@app.get("/realtime/economy")
async def get_realtime_economy():
    """Get real-time economic data."""
    global simulation_engine
    
    if not simulation_engine:
        return {"market": {}, "gini_coefficient": 0.0}
    
    try:
        data = await simulation_engine.get_economic_data()
        return data
    except Exception as e:
        return {"market": {}, "gini_coefficient": 0.0, "error": str(e)}


# Statistics and analytics endpoints
@app.get("/stats/performance")
async def get_performance_stats():
    """Get simulation performance statistics."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        if simulation_engine.scheduler:
            stats = simulation_engine.scheduler.get_performance_stats()
            return stats
        else:
            return {"error": "Scheduler not initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/history")
async def get_simulation_history():
    """Get simulation tick history."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        if simulation_engine.world and simulation_engine.world.tick_history:
            return {"history": simulation_engine.world.tick_history}
        else:
            return {"history": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Utility endpoints
@app.get("/config")
async def get_config():
    """Get current simulation configuration."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        return {"config": simulation_engine.config.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_simulation():
    """Reset the simulation to initial state."""
    global simulation_engine
    
    if not simulation_engine:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    try:
        # Stop current simulation
        await simulation_engine.stop_simulation()
        
        # Reinitialize
        success = await simulation_engine.initialize()
        
        if success:
            return {"status": "reset_complete"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset simulation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Environmental Stimuli endpoints
@app.get("/stimuli/status")
async def get_stimuli_status():
    """Get environmental stimuli system status."""
    try:
        if not simulation_engine:
            raise HTTPException(status_code=404, detail="No active simulation")
        
        status = simulation_engine.get_environmental_stimuli_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stimuli/active")
async def get_active_stimuli():
    """Get currently active environmental stimuli."""
    try:
        if not simulation_engine or not simulation_engine.stimuli_manager:
            raise HTTPException(status_code=404, detail="No active simulation or stimuli manager")
        
        stimuli = simulation_engine.stimuli_manager.get_active_stimuli()
        
        # Convert to JSON-serializable format
        stimuli_data = []
        for stimulus in stimuli:
            stimuli_data.append({
                "id": stimulus.id,
                "type": stimulus.stimulus_type.value,
                "title": stimulus.title,
                "content": stimulus.content[:200] + "..." if len(stimulus.content) > 200 else stimulus.content,
                "source": stimulus.source,
                "timestamp": stimulus.timestamp.isoformat(),
                "intensity": stimulus.intensity.value,
                "sentiment": stimulus.sentiment,
                "keywords": stimulus.keywords,
                "cultural_impact": stimulus.cultural_impact,
                "economic_impact": stimulus.economic_impact,
                "social_impact": stimulus.social_impact
            })
        
        return {
            "count": len(stimuli_data),
            "stimuli": stimuli_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stimuli/by-type/{stimulus_type}")
async def get_stimuli_by_type(stimulus_type: str):
    """Get stimuli filtered by type."""
    try:
        if not simulation_engine or not simulation_engine.stimuli_manager:
            raise HTTPException(status_code=404, detail="No active simulation or stimuli manager")
        
        # Validate stimulus type
        try:
            stimulus_type_enum = StimulusType(stimulus_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid stimulus type: {stimulus_type}")
        
        stimuli = simulation_engine.stimuli_manager.get_stimuli_by_type(stimulus_type_enum)
        
        # Convert to JSON-serializable format
        stimuli_data = []
        for stimulus in stimuli:
            stimuli_data.append({
                "id": stimulus.id,
                "type": stimulus.stimulus_type.value,
                "title": stimulus.title,
                "content": stimulus.content[:200] + "..." if len(stimulus.content) > 200 else stimulus.content,
                "source": stimulus.source,
                "timestamp": stimulus.timestamp.isoformat(),
                "intensity": stimulus.intensity.value,
                "sentiment": stimulus.sentiment,
                "keywords": stimulus.keywords,
                "cultural_impact": stimulus.cultural_impact,
                "economic_impact": stimulus.economic_impact,
                "social_impact": stimulus.social_impact
            })
        
        return {
            "type": stimulus_type,
            "count": len(stimuli_data),
            "stimuli": stimuli_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stimuli/fetch")
async def fetch_stimuli():
    """Manually trigger fetching of environmental stimuli."""
    try:
        if not simulation_engine or not simulation_engine.stimuli_manager:
            raise HTTPException(status_code=404, detail="No active simulation or stimuli manager")
        
        # Fetch stimuli
        stimuli = await simulation_engine.stimuli_manager.fetch_all_stimuli()
        
        return {
            "status": "success",
            "fetched_count": len(stimuli),
            "message": f"Fetched {len(stimuli)} environmental stimuli"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stimuli/divergence")
async def get_cultural_divergence():
    """Get cultural divergence analysis from reality."""
    try:
        if not simulation_engine or not simulation_engine.stimuli_manager:
            raise HTTPException(status_code=404, detail="No active simulation or stimuli manager")
        
        divergence_summary = simulation_engine.stimuli_manager.get_cultural_divergence_summary()
        
        return {
            "cultural_divergence": divergence_summary,
            "interpretation": {
                "mirroring_factor": f"{divergence_summary['mirroring_factor']:.1%} of culture mirrors reality",
                "divergence_rate": f"{divergence_summary['divergence_rate']:.1%} divergence rate per stimulus",
                "reality_baseline": "Baseline patterns from real-world data",
                "future_projection": "Culture evolving toward future version of reality"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with security-aware error messages."""
    # Don't leak internal error details in production
    error_detail = str(exc) if ENVIRONMENT != "production" else "Internal server error"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": error_detail}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
