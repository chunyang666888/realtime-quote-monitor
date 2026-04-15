"""Quote data sources.

The engine is source-agnostic: anything that yields :class:`Quote` objects
works. Two offline sources ship out of the box (no network, no API keys):

* :class:`SimulatedSource` — random-walk ticks, great for demos & CI.
* :class:`CsvReplaySource` — replays a recorded session from disk.

To go live, subclass and yield quotes from your broker's WebSocket / REST
feed; the rest of the engine stays unchanged.
"""
from __future__ import annotations

import csv
import random
from datetime import datetime
from typing import Iterator, List, Optional

from .types import Quote


class SimulatedSource:
    """Generates random-walk ticks for one or more symbols, fully offline."""

    def __init__(
        self,
        symbols: List[str],
        start_prices: Optional[dict] = None,
        volatility: float = 0.01,
        limit: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> None:
        self.symbols = list(symbols)
        self.prices = {s: (start_prices or {}).get(s, 100.0) for s in self.symbols}
        self.prev = dict(self.prices)
        self.volatility = volatility
        self.limit = limit
        self._count = 0
        random.seed(seed)

    def next(self) -> Optional[Quote]:
        if self.limit is not None and self._count >= self.limit:
            return None
        self._count += 1
        sym = random.choice(self.symbols)
        drift = random.gauss(0, self.volatility)
        new_price = round(max(1.0, self.prices[sym] * (1 + drift)), 2)
        quote = Quote(
            symbol=sym,
            price=new_price,
            prev_close=self.prev[sym],
            volume=random.randint(1000, 50000),
            timestamp=datetime.now(),
        )
        self.prev[sym] = self.prices[sym]
        self.prices[sym] = new_price
        return quote


class CsvReplaySource:
    """Replays quotes from a CSV file (``timestamp,symbol,price,prev_close,volume``)."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._rows: List[Quote] = []
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                self._rows.append(
                    Quote(
                        symbol=row["symbol"],
                        price=float(row["price"]),
                        prev_close=float(row.get("prev_close", 0) or 0),
                        volume=int(float(row.get("volume", 0) or 0)),
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                    )
                )
        self._idx = 0

    def next(self) -> Optional[Quote]:
        if self._idx >= len(self._rows):
            return None
        quote = self._rows[self._idx]
        self._idx += 1
        return quote

    def __len__(self) -> int:
        return len(self._rows)
