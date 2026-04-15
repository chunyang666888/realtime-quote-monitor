"""realtime-quote-monitor — a dependency-light auto-watch engine.

Feed it quotes from any source (simulated, CSV replay, or your own broker
WebSocket) and register alert rules (price cross, % change, volume spike,
moving-average cross). Alerts are dispatched to the handlers you attach.
"""

from .types import Quote, Alert
from .engine import Monitor
from .sources import SimulatedSource, CsvReplaySource
from .rules import (
    Rule,
    PriceCrossRule,
    PctChangeRule,
    VolumeSpikeRule,
    MACrossRule,
)

__all__ = [
    "Quote",
    "Alert",
    "Monitor",
    "SimulatedSource",
    "CsvReplaySource",
    "Rule",
    "PriceCrossRule",
    "PctChangeRule",
    "VolumeSpikeRule",
    "MACrossRule",
]
