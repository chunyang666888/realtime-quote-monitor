from datetime import datetime

from monitor.engine import Monitor
from monitor.rules import PriceCrossRule
from monitor.sources import SimulatedSource
from monitor.types import Quote


def test_feed_dispatches_alert_and_collects():
    mon = Monitor()
    received = []
    mon.on_alert(lambda a: received.append(a))
    mon.add_rule(PriceCrossRule("A", 50.0, "up"))

    mon.feed(Quote("A", 40))
    assert received == [] and mon.alerts == []

    mon.feed(Quote("A", 60))
    assert len(received) == 1
    assert len(mon.alerts) == 1
    assert received[0].symbol == "A"


def test_run_consumes_simulated_source():
    src = SimulatedSource(["A", "B"], limit=50, seed=1)
    mon = Monitor()
    mon.add_rule(PriceCrossRule("A", 1e9, "up"))  # never fires
    ticks = mon.run(src)
    assert ticks == 50
    assert mon.alerts == []
