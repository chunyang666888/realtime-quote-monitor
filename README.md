# realtime-quote-monitor
![tests](https://github.com/chunyang666888/realtime-quote-monitor/actions/workflows/ci.yml/badge.svg)


> 自动看盘引擎 — a **dependency-light, source-agnostic auto-watch engine** for stock quotes. Register alert rules (price cross, % change, volume spike, MA cross) and get notified the moment they trigger. Core is **standard-library only**, so it runs anywhere with zero install friction.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#running-tests)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#license)

## Why this repo exists

Recruiters for quant / trading-system roles want to see **real-time systems thinking**: event loops, decoupled data feeds, and rule engines — not just offline scripts. This project shows exactly that: a clean `source → rule → alert` pipeline you can point at a simulated feed today and a live broker WebSocket tomorrow without touching the alert logic.

## Features

- **Pluggable data sources** — anything yielding `Quote` objects works. Ships with `SimulatedSource` (offline demo) and `CsvReplaySource` (replay recorded sessions).
- **Composable alert rules** — `PriceCrossRule`, `PctChangeRule`, `VolumeSpikeRule`, `MACrossRule`. Add your own by subclassing `Rule`.
- **Handler callbacks** — push alerts to console, Slack, email, or a trading desk the same way (`Monitor.on_alert(...)`).
- **Bounded history** — rolling window keeps memory flat during long runs.
- **Zero runtime dependencies** — pure Python stdlib; `pytest` only for tests.

## Installation

```bash
pip install -r requirements.txt   # core needs nothing; pytest is for tests
# or
pip install -e .
```

## Quick start

```python
from monitor.engine import Monitor
from monitor.rules import PriceCrossRule, PctChangeRule, VolumeSpikeRule, MACrossRule
from monitor.sources import SimulatedSource

mon = Monitor()
mon.on_alert(lambda a: print(f"ALERT {a.symbol}: {a.message}"))

mon.add_rule(PriceCrossRule("600519", 1710.0, "up"))
mon.add_rule(PctChangeRule("000001", 2.0, "up"))
mon.add_rule(VolumeSpikeRule("300750", multiplier=2.5, window=10))
mon.add_rule(MACrossRule("000001", fast=5, slow=15, direction="golden"))

src = SimulatedSource(["600519", "000001", "300750"],
                      start_prices={"600519": 1700.0}, limit=400, seed=42)
mon.run(src)
```

Or run the bundled demo:

```bash
python examples/auto_watch_demo.py
```

## Architecture

```
        ┌─────────────┐   Quote   ┌──────────┐   Alert   ┌──────────────┐
Source ─▶│  Monitor   │─────────▶│  Rules   │─────────▶│  Handlers    │
        │ (loop/fifo) │           │ (evaluate)│          │ (log/push/…) │
        └─────────────┘           └──────────┘           └──────────────┘
```

| Module | Responsibility |
|--------|----------------|
| `types.py`     | `Quote`, `Alert` data structures |
| `sources.py`   | `SimulatedSource`, `CsvReplaySource` |
| `rules.py`     | `Rule` base + 4 built-in rules |
| `engine.py`    | `Monitor` loop, history, handler dispatch |

## Going live

The engine never assumes where quotes come from. To watch a real market, subclass a source and yield `Quote` objects — e.g. a `WebSocketSource` wrapping your broker's stream, or an HTTP poller. Everything else (rules, alerts, handlers) stays unchanged.

```python
class MyBrokerSource:
    def next(self) -> Optional[Quote]:
        raw = my_ws.recv()          # your broker's payload
        return Quote(raw["code"], float(raw["last"]), float(raw["prevClose"]))
```

## Running tests

```bash
pytest -q
```

## Project structure

```
realtime-quote-monitor/
├── monitor/
│   ├── __init__.py
│   ├── types.py
│   ├── sources.py
│   ├── rules.py
│   └── engine.py
├── examples/
│   └── auto_watch_demo.py
├── tests/
│   ├── test_rules.py
│   ├── test_engine.py
│   └── test_sources.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## License

MIT — free for personal and commercial use.
