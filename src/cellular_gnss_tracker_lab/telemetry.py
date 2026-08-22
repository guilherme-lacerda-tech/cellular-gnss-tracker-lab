from __future__ import annotations

from dataclasses import dataclass

from cellular_gnss_tracker_lab.state_machine import backoff_seconds


@dataclass(frozen=True)
class TelemetryPacket:
    sequence: int
    lat: float
    lon: float
    delivered: bool = True


def analyze_delivery(packets: list[TelemetryPacket]) -> dict[str, object]:
    delivered = [packet for packet in packets if packet.delivered]
    seen: set[int] = set()
    duplicates = 0
    out_of_order = 0
    last_sequence = -1
    for packet in delivered:
        if packet.sequence in seen:
            duplicates += 1
        if packet.sequence < last_sequence:
            out_of_order += 1
        seen.add(packet.sequence)
        last_sequence = max(last_sequence, packet.sequence)

    network_losses = len([packet for packet in packets if not packet.delivered])
    reconnects = 1 if network_losses and delivered else 0
    return {
        "received": len(delivered),
        "duplicates": duplicates,
        "out_of_order": out_of_order,
        "network_losses": network_losses,
        "reconnects": reconnects,
        "watchdog_kicks": network_losses,
        "recovery_status": "recovered" if reconnects else "stable",
        "next_backoff_seconds": backoff_seconds(network_losses),
    }


def synthetic_delivery_scenario(name: str) -> list[TelemetryPacket]:
    base = [
        TelemetryPacket(1, -23.5505, -46.6333),
        TelemetryPacket(2, -23.5506, -46.6334),
        TelemetryPacket(3, -23.5507, -46.6335),
    ]
    if name == "duplicate_packet":
        return [*base, base[1]]
    if name == "out_of_order_packet":
        return [base[0], base[2], base[1]]
    if name == "network_loss_reconnect":
        return [base[0], TelemetryPacket(2, -23.5506, -46.6334, delivered=False), base[2]]
    if name == "normal_delivery":
        return base
    valid = "duplicate_packet, network_loss_reconnect, normal_delivery, out_of_order_packet"
    raise ValueError(f"Unknown telemetry scenario '{name}'. Valid scenarios: {valid}")
