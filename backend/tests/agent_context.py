from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class AgentTestContext:
    """Provides deterministic context for AI agent testing.

    Seed and mock clock can be derived from agent identifiers to ensure
    reproducible behavior across runs without relying on global state.
    """

    agent_id: str
    seed: int
    mock_time: datetime

    @classmethod
    def from_agent(cls, agent_id: str) -> "AgentTestContext":
        # Use stable hash for deterministic seeds across runs
        seed = int.from_bytes(hashlib.sha256(agent_id.encode()).digest()[:4], 'big') % 1_000_000
        return cls(agent_id=agent_id, seed=seed, mock_time=datetime(2024, 1, 1))

