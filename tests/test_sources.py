import os
import tempfile
from datetime import datetime

from monitor.sources import SimulatedSource, CsvReplaySource


def test_simulated_source_yields_valid_quotes():
    src = SimulatedSource(["600519", "000001"], start_prices={"600519": 1700.0}, limit=20, seed=3)
    seen = set()
    for _ in range(20):
        quote = src.next()
        assert quote is not None
        assert quote.symbol in {"600519", "000001"}
        assert quote.price > 0
        seen.add(quote.symbol)
    assert src.next() is None  # exhausted
    assert seen == {"600519", "000001"}


def test_csv_replay_source_preserves_order():
    csv_text = (
        "timestamp,symbol,price,prev_close,volume\n"
        "2026-01-01T09:30:00,600519,1700.0,1690.0,1000\n"
        "2026-01-01T09:31:00,000001,12.0,11.9,2000\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as fh:
        fh.write(csv_text)
        path = fh.name
    try:
        src = CsvReplaySource(path)
        assert len(src) == 2
        a = src.next()
        b = src.next()
        assert a.symbol == "600519" and a.price == 1700.0
        assert b.symbol == "000001" and b.volume == 2000
        assert src.next() is None
    finally:
        os.unlink(path)
