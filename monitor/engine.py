"""The monitoring loop that ties sources, rules, and alert handlers together."""
from __future__ import annotations

from collections import deque
from typing import Callable, List, Optional

from .rules import Rule
from .sources import SimulatedSource
from .types import Alert, Quote

AlertHandler = Callable[[Alert], None]


class Monitor:
    """Feeds quotes through registered rules and dispatches alerts."""

    def __init__(self, max_history: int = 500) -> None:
        self.rules: List[Rule] = []
        self.history: deque = deque(maxlen=max_history)
        self.handlers: List[AlertHandler] = []
        self.alerts: List[Alert] = []

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)

    def on_alert(self, handler: AlertHandler) -> None:
        """Register a callback invoked for every fired alert (e.g. log / push)."""
        self.handlers.append(handler)

    def feed(self, quote: Quote) -> List[Alert]:
        """Process a single quote; returns the alerts fired for it."""
        self.history.append(quote)
        fired: List[Alert] = []
        for rule in self.rules:
            alert = rule.evaluate(quote, list(self.history))
            if alert:
                fired.append(alert)
                self.alerts.append(alert)
                for handler in self.handlers:
                    handler(alert)
        return fired

    def run(self, source: SimulatedSource, n: Optional[int] = None) -> int:
        """Consume the source until it is exhausted (or ``n`` ticks). Returns tick count."""
        count = 0
        while True:
            quote = source.next()
            if quote is None:
                break
            self.feed(quote)
            count += 1
            if n is not None and count >= n:
                break
        return count
