"""Auto-watch demo: simulate live ticks for a few names and fire alerts.

Runs fully offline (no network, no API keys). Swap ``SimulatedSource`` for a
real broker feed (or ``CsvReplaySource``) in production.
"""
from monitor.engine import Monitor
from monitor.rules import MACrossRule, PctChangeRule, PriceCrossRule, VolumeSpikeRule
from monitor.sources import SimulatedSource


def printer(alert):
    print(f"[ALERT {alert.timestamp:%H:%M:%S}] {alert.symbol}: {alert.message}")


def main():
    src = SimulatedSource(
        ["600519", "000001", "300750"],
        start_prices={"600519": 1700.0, "000001": 12.0, "300750": 180.0},
        volatility=0.015,
        limit=400,
        seed=42,
    )
    mon = Monitor()
    mon.on_alert(printer)

    # Price crosses a level
    mon.add_rule(PriceCrossRule("600519", 1710.0, "up"))
    # Intraday move exceeds 2%
    mon.add_rule(PctChangeRule("000001", 2.0, "up"))
    # Volume 2.5x its rolling average
    mon.add_rule(VolumeSpikeRule("300750", multiplier=2.5, window=10))
    # Golden cross on the 5/15 MA
    mon.add_rule(MACrossRule("000001", fast=5, slow=15, direction="golden"))

    ticks = mon.run(src)
    print(f"\nSimulated {ticks} ticks — {len(mon.alerts)} alert(s) fired.")


if __name__ == "__main__":
    main()
