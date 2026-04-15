"""Alert rules. Each rule inspects the latest quote (and recent history)
and optionally returns an :class:`Alert`."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from .types import Alert, Quote


class Rule(ABC):
    """Base class for alert rules."""

    name: str = "rule"

    @abstractmethod
    def evaluate(self, quote: Quote, history: List[Quote]) -> Optional[Alert]:
        raise NotImplementedError


class PriceCrossRule(Rule):
    """Fires when a symbol's price crosses a fixed threshold."""

    def __init__(self, symbol: str, threshold: float, direction: str = "up") -> None:
        self.symbol = symbol
        self.threshold = threshold
        self.direction = direction
        self.name = f"price_cross_{direction}_{threshold}"

    def evaluate(self, quote: Quote, history: List[Quote]) -> Optional[Alert]:
        if quote.symbol != self.symbol:
            return None
        if self.direction == "up" and quote.price >= self.threshold:
            return Alert(
                quote.symbol,
                self.name,
                f"{quote.symbol} crossed UP to {quote.price} (>= {self.threshold})",
                quote.price,
            )
        if self.direction == "down" and quote.price <= self.threshold:
            return Alert(
                quote.symbol,
                self.name,
                f"{quote.symbol} crossed DOWN to {quote.price} (<= {self.threshold})",
                quote.price,
            )
        return None


class PctChangeRule(Rule):
    """Fires when a symbol's intraday % change exceeds a bound."""

    def __init__(self, symbol: str, threshold_pct: float, direction: str = "up") -> None:
        self.symbol = symbol
        self.threshold_pct = threshold_pct
        self.direction = direction
        self.name = f"pct_change_{direction}_{threshold_pct}"

    def evaluate(self, quote: Quote, history: List[Quote]) -> Optional[Alert]:
        if quote.symbol != self.symbol:
            return None
        ch = quote.pct_change
        if self.direction == "up" and ch >= self.threshold_pct:
            return Alert(
                quote.symbol,
                self.name,
                f"{quote.symbol} up {ch:.2f}% (>= {self.threshold_pct}%)",
                quote.price,
            )
        if self.direction == "down" and ch <= -self.threshold_pct:
            return Alert(
                quote.symbol,
                self.name,
                f"{quote.symbol} down {ch:.2f}% (<= -{self.threshold_pct}%)",
                quote.price,
            )
        return None


class VolumeSpikeRule(Rule):
    """Fires when volume exceeds ``multiplier`` x the rolling average."""

    def __init__(self, symbol: str, multiplier: float = 3.0, window: int = 20) -> None:
        self.symbol = symbol
        self.multiplier = multiplier
        self.window = window
        self.name = f"volume_spike_{multiplier}x_{window}"

    def evaluate(self, quote: Quote, history: List[Quote]) -> Optional[Alert]:
        if quote.symbol != self.symbol:
            return None
        recent = [q.volume for q in history if q.symbol == self.symbol][-self.window :]
        if len(recent) < self.window:
            return None
        avg = sum(recent) / len(recent)
        if avg > 0 and quote.volume >= self.multiplier * avg:
            return Alert(
                quote.symbol,
                self.name,
                f"{quote.symbol} volume spike {quote.volume} (>= {self.multiplier}x avg {avg:.0f})",
                quote.price,
            )
        return None


def _sma(prices: List[float], n: int) -> float:
    window = prices[-n:]
    return sum(window) / len(window)


class MACrossRule(Rule):
    """Fires on a fast/slow moving-average cross (golden or death)."""

    def __init__(self, symbol: str, fast: int = 5, slow: int = 20, direction: str = "golden") -> None:
        self.symbol = symbol
        self.fast = fast
        self.slow = slow
        self.direction = direction
        self.name = f"ma_cross_{direction}_{fast}_{slow}"

    def evaluate(self, quote: Quote, history: List[Quote]) -> Optional[Alert]:
        if quote.symbol != self.symbol:
            return None
        prices = [q.price for q in history if q.symbol == self.symbol] + [quote.price]
        if len(prices) <= self.slow + 1:
            return None
        fast_prev = _sma(prices[:-1], self.fast)
        fast_cur = _sma(prices, self.fast)
        slow_prev = _sma(prices[:-1], self.slow)
        slow_cur = _sma(prices, self.slow)
        if self.direction == "golden" and fast_prev <= slow_prev and fast_cur > slow_cur:
            return Alert(quote.symbol, self.name, f"{quote.symbol} GOLDEN cross (MA{self.fast} > MA{self.slow})", quote.price)
        if self.direction == "death" and fast_prev >= slow_prev and fast_cur < slow_cur:
            return Alert(quote.symbol, self.name, f"{quote.symbol} DEATH cross (MA{self.fast} < MA{self.slow})", quote.price)
        return None
