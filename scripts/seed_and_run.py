#!/usr/bin/env python3
"""
Seed and run script for The Cognisphere simulation.

Provides command-line interface for running simulations with different
configurations and presets for testing and benchmarking.
"""

import os
import sys

# Reproducibility: Python randomizes string hashing per-process (PYTHONHASHSEED),
# which makes set/dict iteration order vary between runs. For deterministic
# seeded simulations we pin the hash seed and re-exec once before doing any work.
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)

import asyncio
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from simulation.engine import SimulationEngine, SimulationConfig
from adapters import LLMMode


def load_stimuli_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load external stimuli from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load stimuli file {file_path}: {e}")
        return None


def create_preset_config(preset: str, **kwargs) -> SimulationConfig:
    """Create simulation configuration from preset."""
    presets = {
        "lab": SimulationConfig(
            num_agents=100,
            seed=42,
            max_ticks=300,
            llm_mode=LLMMode.MOCK,
            tick_duration_ms=50,
            agents_per_tick=25,
            interactions_per_tick=50,
            snapshot_frequency=50,
            memory_backend="networkx",
            vector_backend="faiss"
        ),
        "demo": SimulationConfig(
            num_agents=300,
            seed=123,
            max_ticks=1000,
            llm_mode=LLMMode.MOCK,
            tick_duration_ms=100,
            agents_per_tick=50,
            interactions_per_tick=100,
            snapshot_frequency=100,
            memory_backend="networkx",
            vector_backend="faiss"
        ),
        "production": SimulationConfig(
            num_agents=500,
            seed=None,
            max_ticks=10000,
            llm_mode=LLMMode.OPENAI,
            llm_model="gpt-3.5-turbo",
            llm_temperature=0.3,
            tick_duration_ms=200,
            agents_per_tick=100,
            interactions_per_tick=200,
            snapshot_frequency=200,
            memory_backend="neo4j",
            vector_backend="chroma"
        ),
        "benchmark": SimulationConfig(
            num_agents=1000,
            seed=42,
            max_ticks=5000,
            llm_mode=LLMMode.MOCK,
            tick_duration_ms=10,
            agents_per_tick=200,
            interactions_per_tick=500,
            snapshot_frequency=100,
            memory_backend="networkx",
            vector_backend="faiss"
        )
    }
    
    if preset not in presets:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(presets.keys())}")
    
    config = presets[preset]
    
    # Override with kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config


async def run_simulation(config: SimulationConfig, verbose: bool = False) -> Dict[str, Any]:
    """Run a simulation with the given configuration."""
    print(f" Starting simulation with {config.num_agents} agents...")
    print(f"   Seed: {config.seed}")
    print(f"   Max ticks: {config.max_ticks}")
    print(f"   LLM mode: {config.llm_mode.value}")
    print(f"   Memory backend: {config.memory_backend}")
    print(f"   Vector backend: {config.vector_backend}")
    
    # Create simulation engine
    engine = SimulationEngine(config)
    
    # Initialize
    print(" Initializing simulation engine...")
    success = await engine.initialize()
    if not success:
        raise RuntimeError("Failed to initialize simulation engine")
    
    # Run simulation
    print("  Running simulation...")
    start_time = time.time()
    
    success = await engine.run_simulation()
    if not success:
        raise RuntimeError("Simulation failed")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Get final statistics
    final_summary = engine.world.get_world_summary()
    
    print(f" Simulation completed in {duration:.2f} seconds")
    print(f"   Total ticks: {engine.world.current_tick}")
    print(f"   Final agents: {len(engine.world.agents)}")
    print(f"   Final factions: {len(engine.world.factions)}")
    print(f"   Total myths: {len(engine.world.culture.myths)}")
    print(f"   Active norms: {len(engine.world.culture.active_norms)}")
    print(f"   Total trades: {len(engine.world.economy.trade_history)}")
    print(f"   Gini coefficient: {engine.world.economy.gini_coefficient:.3f}")

    # Social & negotiation dynamics
    social = engine.world.social_engine.get_social_summary()
    negotiation = engine.world.negotiation_engine.get_negotiation_summary()
    memory = engine.world.memory_manager.get_memory_statistics()
    print(f"   Alliances formed: {social['total_alliances']}")
    print(f"   Betrayals: {social['total_betrayals']}")
    print(f"   Institutions: {social['total_institutions']}")
    print(f"   Avg reputation: {social['average_reputation']:.3f}")
    print(f"   Negotiations (ok/total): {negotiation['successful_negotiations']}/{negotiation['completed_negotiations']}")
    print(f"   Market clearings: {negotiation['market_clearings']}")
    print(f"   World memories (graph+vector): {memory['total_memories']}")

    # Performance metrics
    if engine.scheduler:
        perf_stats = engine.scheduler.get_performance_stats()
        print(f"   Avg tick duration: {perf_stats.get('avg_tick_duration', 0):.2f}ms")
        print(f"   Total duration: {perf_stats.get('total_duration', 0):.2f}s")
    
    # Cleanup
    engine.cleanup()
    
    return {
        "duration": duration,
        "ticks": engine.world.current_tick,
        "agents": len(engine.world.agents),
        "factions": len(engine.world.factions),
        "myths": len(engine.world.culture.myths),
        "norms": len(engine.world.culture.active_norms),
        "trades": len(engine.world.economy.trade_history),
        "gini_coefficient": engine.world.economy.gini_coefficient,
        "performance": engine.scheduler.get_performance_stats() if engine.scheduler else {},
        "summary": final_summary
    }


async def benchmark_simulation(config: SimulationConfig, runs: int = 5) -> Dict[str, Any]:
    """Run multiple simulations for benchmarking."""
    print(f" Running benchmark with {runs} iterations...")
    
    results = []
    total_start = time.time()
    
    for i in range(runs):
        print(f"\n--- Run {i + 1}/{runs} ---")
        run_config = SimulationConfig(**config.to_dict())
        run_config.seed = (config.seed or 42) + i  # Different seed for each run
        
        try:
            result = await run_simulation(run_config, verbose=False)
            results.append(result)
        except Exception as e:
            print(f" Run {i + 1} failed: {e}")
            continue
    
    total_duration = time.time() - total_start
    
    if not results:
        raise RuntimeError("All benchmark runs failed")
    
    # Calculate statistics
    durations = [r["duration"] for r in results]
    ticks = [r["ticks"] for r in results]
    agents = [r["agents"] for r in results]
    myths = [r["myths"] for r in results]
    trades = [r["trades"] for r in results]
    gini_coeffs = [r["gini_coefficient"] for r in results]
    
    benchmark_results = {
        "runs": len(results),
        "total_duration": total_duration,
        "avg_duration": sum(durations) / len(durations),
        "min_duration": min(durations),
        "max_duration": max(durations),
        "avg_ticks": sum(ticks) / len(ticks),
        "avg_agents": sum(agents) / len(agents),
        "avg_myths": sum(myths) / len(myths),
        "avg_trades": sum(trades) / len(trades),
        "avg_gini": sum(gini_coeffs) / len(gini_coeffs),
        "results": results
    }
    
    print(f"\n Benchmark Results:")
    print(f"   Runs completed: {benchmark_results['runs']}")
    print(f"   Total time: {benchmark_results['total_duration']:.2f}s")
    print(f"   Avg duration: {benchmark_results['avg_duration']:.2f}s")
    print(f"   Duration range: {benchmark_results['min_duration']:.2f}s - {benchmark_results['max_duration']:.2f}s")
    print(f"   Avg ticks: {benchmark_results['avg_ticks']:.1f}")
    print(f"   Avg myths: {benchmark_results['avg_myths']:.1f}")
    print(f"   Avg trades: {benchmark_results['avg_trades']:.1f}")
    print(f"   Avg Gini: {benchmark_results['avg_gini']:.3f}")
    
    return benchmark_results


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run The Cognisphere simulation")
    
    # Preset selection
    parser.add_argument("--preset", choices=["lab", "demo", "production", "benchmark"], 
                       default="lab", help="Simulation preset configuration")
    
    # Basic parameters
    parser.add_argument("--agents", type=int, help="Number of agents")
    parser.add_argument("--ticks", type=int, help="Maximum number of ticks")
    parser.add_argument("--seed", type=int, help="Random seed")
    
    # LLM settings
    parser.add_argument("--llm-mode", choices=["mock", "openai"], default="mock",
                       help="LLM mode")
    parser.add_argument("--llm-model", default="gpt-3.5-turbo", help="LLM model")
    parser.add_argument("--llm-temperature", type=float, default=0.3, help="LLM temperature")
    parser.add_argument("--llm-api-key", help="OpenAI API key")
    
    # Performance settings
    parser.add_argument("--tick-duration", type=int, help="Tick duration in milliseconds")
    parser.add_argument("--agents-per-tick", type=int, help="Agents to process per tick")
    parser.add_argument("--interactions-per-tick", type=int, help="Interactions per tick")
    
    # Storage settings
    parser.add_argument("--memory-backend", choices=["networkx", "neo4j"], 
                       default="networkx", help="Memory backend")
    parser.add_argument("--vector-backend", choices=["faiss", "chroma"], 
                       default="faiss", help="Vector backend")
    
    # External stimuli
    parser.add_argument("--stimuli", help="Path to stimuli JSON file")
    
    # Output settings
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--snapshot-dir", default="snapshots", help="Snapshot directory")
    
    # Benchmark mode
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark mode")
    parser.add_argument("--runs", type=int, default=5, help="Number of benchmark runs")
    
    # Other options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create configuration
    config_kwargs = {}
    if args.agents:
        config_kwargs["num_agents"] = args.agents
    if args.ticks:
        config_kwargs["max_ticks"] = args.ticks
    if args.seed:
        config_kwargs["seed"] = args.seed
    if args.tick_duration:
        config_kwargs["tick_duration_ms"] = args.tick_duration
    if args.agents_per_tick:
        config_kwargs["agents_per_tick"] = args.agents_per_tick
    if args.interactions_per_tick:
        config_kwargs["interactions_per_tick"] = args.interactions_per_tick
    if args.memory_backend:
        config_kwargs["memory_backend"] = args.memory_backend
    if args.vector_backend:
        config_kwargs["vector_backend"] = args.vector_backend
    if args.snapshot_dir:
        config_kwargs["snapshot_directory"] = args.snapshot_dir
    
    # LLM settings
    if args.llm_mode:
        config_kwargs["llm_mode"] = LLMMode(args.llm_mode)
    if args.llm_model:
        config_kwargs["llm_model"] = args.llm_model
    if args.llm_temperature:
        config_kwargs["llm_temperature"] = args.llm_temperature
    if args.llm_api_key:
        config_kwargs["llm_api_key"] = args.llm_api_key
    
    # External stimuli
    if args.stimuli:
        config_kwargs["stimuli_file"] = args.stimuli
    
    config = create_preset_config(args.preset, **config_kwargs)
    
    try:
        if args.benchmark:
            # Benchmark mode
            results = await benchmark_simulation(config, args.runs)
        else:
            # Single simulation
            results = await run_simulation(config, args.verbose)
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f" Results saved to {args.output}")
        
        print("\n Simulation completed successfully!")
        
    except Exception as e:
        print(f" Simulation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
