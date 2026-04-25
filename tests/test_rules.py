from datetime import datetime

from monitor.rules import (
    PriceCrossRule,
    PctChangeRule,
    VolumeSpikeRule,
    MACrossRule,
)
from monitor.types import Quote


def q(symbol, price, prev_close=0.0, volume=0, ts=None):
    return Quote(symbol, price, prev_close, volume, ts or datetime(2026, 1, 1))


def test_price_cross_up():
    rule = PriceCrossRule("A", 100.0, "up")
    assert rule.evaluate(q("A", 105), []) is not None
    assert rule.evaluate(q("A", 95), []) is None
    assert rule.evaluate(q("B", 105), []) is None  # wrong symbol


def test_price_cross_down():
    rule = PriceCrossRule("A", 100.0, "down")
    assert rule.evaluate(q("A", 95), []) is not None
    assert rule.evaluate(q("A", 105), []) is None


def test_pct_change_up_and_down():
    up = PctChangeRule("A", 2.0, "up")
    assert up.evaluate(q("A", 103, prev_close=100), []) is not None
    assert up.evaluate(q("A", 101, prev_close=100), []) is None

    down = PctChangeRule("A", 2.0, "down")
    assert down.evaluate(q("A", 98, prev_close=100), []) is not None


def test_volume_spike():
    rule = VolumeSpikeRule("A", multiplier=3.0, window=3)
    hist = [q("A", 10, volume=100) for _ in range(3)]
    alert = rule.evaluate(q("A", 10, volume=500), hist)
    assert alert is not None
    # not enough history yet
    assert rule.evaluate(q("A", 10, volume=500), hist[:1]) is None
    # normal volume
    assert rule.evaluate(q("A", 10, volume=150), hist) is None


def test_ma_golden_cross():
    rule = MACrossRule("A", fast=2, slow=3, direction="golden")
    hist = [q("A", p) for p in (10, 10, 10, 10)]
    alert = rule.evaluate(q("A", 20), hist)
    assert alert is not None and "GOLDEN" in alert.message


def test_ma_death_cross():
    rule = MACrossRule("A", fast=2, slow=3, direction="death")
    hist = [q("A", p) for p in (20, 20, 20, 20)]
    alert = rule.evaluate(q("A", 5), hist)
    assert alert is not None and "DEATH" in alert.message
