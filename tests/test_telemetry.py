import pytest

from cellular_gnss_tracker_lab.telemetry import analyze_delivery, synthetic_delivery_scenario


def test_duplicate_packet_is_counted() -> None:
    summary = analyze_delivery(synthetic_delivery_scenario("duplicate_packet"))

    assert summary["duplicates"] == 1
    assert summary["recovery_status"] == "stable"


def test_out_of_order_packet_is_counted() -> None:
    summary = analyze_delivery(synthetic_delivery_scenario("out_of_order_packet"))

    assert summary["out_of_order"] == 1


def test_network_loss_reconnect_tracks_recovery_and_backoff() -> None:
    summary = analyze_delivery(synthetic_delivery_scenario("network_loss_reconnect"))

    assert summary["network_losses"] == 1
    assert summary["reconnects"] == 1
    assert summary["watchdog_kicks"] == 1
    assert summary["next_backoff_seconds"] == 2
    assert summary["recovery_status"] == "recovered"


def test_unknown_telemetry_scenario_errors() -> None:
    with pytest.raises(ValueError, match="Unknown telemetry scenario"):
        synthetic_delivery_scenario("real_world")
