from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AtResponse:
    command: str
    ok: bool
    lines: list[str]
    error: str | None = None
    timed_out: bool = False


def parse_at_response(command: str, raw: str, timed_out: bool = False) -> AtResponse:
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if timed_out:
        return AtResponse(command=command, ok=False, lines=lines, error="timeout", timed_out=True)
    if any(line == "OK" for line in lines):
        return AtResponse(command=command, ok=True, lines=[line for line in lines if line != "OK"])
    error_line = next((line for line in lines if line.startswith("ERROR") or line.startswith("+CME ERROR")), None)
    return AtResponse(command=command, ok=False, lines=lines, error=error_line or "missing OK")


def parse_gnss_position(raw: str) -> tuple[float, float, int] | None:
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("+QGPSLOC:"):
            continue
        payload = line.split(":", 1)[1].strip()
        parts = [part.strip() for part in payload.split(",")]
        if len(parts) < 4:
            return None
        latitude = float(parts[1])
        longitude = float(parts[2])
        quality = int(parts[3])
        return latitude, longitude, quality
    return None


def should_retry(response: AtResponse) -> bool:
    return response.timed_out or response.error is not None

