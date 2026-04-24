"""Core data structures for realtime quote monitoring."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Quote:
    """A single market snapshot for one symbol."""

    symbol: str
    price: float
    prev_close: float = 0.0
    volume: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def pct_change(self) -> float:
        """Percentage change vs previous close (0.0 when unknown)."""
        if self.prev_close <= 0:
            return 0.0
        return (self.price / self.prev_close - 1.0) * 100.0


@dataclass
class Alert:
    """An event emitted by a rule when its condition is met."""

    symbol: str
    rule: str
    message: str
    price: float
    timestamp: datetime = field(default_factory=datetime.now)
