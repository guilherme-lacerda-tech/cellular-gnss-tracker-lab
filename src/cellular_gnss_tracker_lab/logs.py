from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LogEvent:
    timestamp: str
    state: str
    event: str
    detail: str
    next_state: str | None = None


def parse_log_line(line: str) -> LogEvent:
    payload = json.loads(line)
    return LogEvent(
        timestamp=payload["timestamp"],
        state=payload["state"],
        event=payload["event"],
        detail=payload.get("detail", ""),
        next_state=payload.get("next_state"),
    )


def parse_log_file(path: str | Path) -> list[LogEvent]:
    return [
        parse_log_line(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def analyze_events(events: list[LogEvent]) -> dict[str, object]:
    state_counts: dict[str, int] = {}
    failures: list[str] = []
    for event in events:
        state_counts[event.state] = state_counts.get(event.state, 0) + 1
        if event.event in {"TIMEOUT", "NETWORK_LOSS", "GNSS_NO_FIX", "TRANSMISSION_FAILURE"}:
            failures.append(event.event)
    return {
        "event_count": len(events),
        "state_counts": state_counts,
        "failures": failures,
        "recovered": bool(failures)
        and any(event.state == "SLEEP_WAIT" or event.next_state == "SLEEP_WAIT" for event in events),
    }


def write_synthetic_log(path: str | Path, history: list[dict[str, object]]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for index, row in enumerate(history):
        lines.append(
            json.dumps(
                {
                    "timestamp": f"2026-08-13T12:00:{index:02d}Z",
                    "state": row["state"],
                    "event": row["event"],
                    "next_state": row["next_state"],
                    "detail": row["detail"],
                },
                sort_keys=True,
            )
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
