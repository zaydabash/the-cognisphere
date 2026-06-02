"""
Storage adapters for persistent data management.

Provides adapters for different storage backends including SQLite,
PostgreSQL, and other database systems for simulation data persistence.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

import aiosqlite


@dataclass
class StorageConfig:
    """Configuration for storage adapters."""

    database_url: str = "sqlite:///simulation.db"
    connection_pool_size: int = 10
    timeout: int = 30


class StorageAdapter(ABC):
    """Abstract base class for storage adapters."""

    @abstractmethod
    async def save_simulation_state(self, simulation_id: str, state: Dict[str, Any]) -> bool:
        """Save simulation state."""
        pass

    @abstractmethod
    async def load_simulation_state(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Load simulation state."""
        pass

    @abstractmethod
    async def save_agent_data(self, agent_id: str, data: Dict[str, Any]) -> bool:
        """Save agent data."""
        pass

    @abstractmethod
    async def load_agent_data(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent data."""
        pass

    @abstractmethod
    async def save_cultural_data(self, data: Dict[str, Any]) -> bool:
        """Save cultural data."""
        pass

    @abstractmethod
    async def load_cultural_data(self) -> Optional[Dict[str, Any]]:
        """Load cultural data."""
        pass


class SQLiteStorageAdapter(StorageAdapter):
    """SQLite storage adapter for simulation data."""

    def __init__(self, config: StorageConfig):
        self.config = config
        self.db_path = self._extract_db_path()
        self._initialized = False

    def _extract_db_path(self) -> str:
        """Extract database path from URL."""
        if self.config.database_url.startswith("sqlite:///"):
            return self.config.database_url[10:]  # Remove "sqlite:///"
        else:
            return "simulation.db"

    async def _ensure_initialized(self):
        """Ensure database is initialized with required tables."""
        if self._initialized:
            return

        async with aiosqlite.connect(self.db_path) as db:
            # Create tables
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_states (
                    id TEXT PRIMARY KEY,
                    state_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_data (
                    agent_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS cultural_data (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            await db.commit()

        self._initialized = True

    async def save_simulation_state(self, simulation_id: str, state: Dict[str, Any]) -> bool:
        """Save simulation state to database."""
        try:
            await self._ensure_initialized()

            state_json = json.dumps(state)

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO simulation_states (id, state_data, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                    (simulation_id, state_json),
                )
                await db.commit()

            return True
        except Exception as e:
            print(f"Error saving simulation state: {e}")
            return False

    async def load_simulation_state(self, simulation_id: str) -> Optional[Dict[str, Any]]:
        """Load simulation state from database."""
        try:
            await self._ensure_initialized()

            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    """
                    SELECT state_data FROM simulation_states WHERE id = ?
                """,
                    (simulation_id,),
                ) as cursor:
                    row = await cursor.fetchone()

                    if row:
                        return json.loads(row[0])
                    else:
                        return None
        except Exception as e:
            print(f"Error loading simulation state: {e}")
            return None

    async def save_agent_data(self, agent_id: str, data: Dict[str, Any]) -> bool:
        """Save agent data to database."""
        try:
            await self._ensure_initialized()

            data_json = json.dumps(data)

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO agent_data (agent_id, data, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                    (agent_id, data_json),
                )
                await db.commit()

            return True
        except Exception as e:
            print(f"Error saving agent data: {e}")
            return False

    async def load_agent_data(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent data from database."""
        try:
            await self._ensure_initialized()

            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    """
                    SELECT data FROM agent_data WHERE agent_id = ?
                """,
                    (agent_id,),
                ) as cursor:
                    row = await cursor.fetchone()

                    if row:
                        return json.loads(row[0])
                    else:
                        return None
        except Exception as e:
            print(f"Error loading agent data: {e}")
            return None

    async def save_cultural_data(self, data: Dict[str, Any]) -> bool:
        """Save cultural data to database."""
        try:
            await self._ensure_initialized()

            data_json = json.dumps(data)

            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO cultural_data (id, data)
                    VALUES (?, ?)
                """,
                    ("current", data_json),
                )
                await db.commit()

            return True
        except Exception as e:
            print(f"Error saving cultural data: {e}")
            return False

    async def load_cultural_data(self) -> Optional[Dict[str, Any]]:
        """Load cultural data from database."""
        try:
            await self._ensure_initialized()

            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    """
                    SELECT data FROM cultural_data WHERE id = ?
                """,
                    ("current",),
                ) as cursor:
                    row = await cursor.fetchone()

                    if row:
                        return json.loads(row[0])
                    else:
                        return None
        except Exception as e:
            print(f"Error loading cultural data: {e}")
            return None


class StorageAdapterFactory:
    """Factory for creating storage adapters."""

    @staticmethod
    def create_adapter(config: StorageConfig) -> StorageAdapter:
        """Create storage adapter based on configuration."""
        database_url = config.database_url

        if database_url.startswith("sqlite://"):
            return SQLiteStorageAdapter(config)
        else:
            raise ValueError(f"Unsupported database URL: {database_url}")
