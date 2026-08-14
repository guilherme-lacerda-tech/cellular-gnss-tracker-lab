import pytest

from cellular_gnss_tracker_lab.state_machine import (
    Event,
    TrackerConfig,
    TrackerState,
    backoff_seconds,
    run_events,
    run_scenario,
    scenario_names,
    transition,
    TrackerContext,
)


def test_required_scenarios_exist() -> None:
    assert set(scenario_names()) == {
        "gnss_no_fix",
        "modem_timeout",
        "network_failure",
        "normal_operation",
        "registration_denied",
        "recovery",
        "transmission_failure",
    }


def test_normal_operation_reaches_sleep_and_transmits() -> None:
    context = run_scenario("normal_operation")
    assert context.history[-1]["next_state"] == "SLEEP_WAIT"
    assert context.transmissions == 1
    assert context.last_position == (-23.5505, -46.6333)


def test_network_failure_resets_modem_and_recovers() -> None:
    context = run_scenario("network_failure")
    assert context.modem_resets == 1
    assert context.watchdog_kicks == 1
    assert context.transmissions == 1


def test_registration_denied_uses_recovery_path() -> None:
    context = run_scenario("registration_denied")
    assert any(row["event"] == "REGISTRATION_DENIED" for row in context.history)
    assert context.modem_resets == 1
    assert context.transmissions == 1


def test_gnss_no_fix_retries_gnss_without_modem_reset() -> None:
    context = run_scenario("gnss_no_fix")
    assert context.modem_resets == 0
    assert any(row["event"] == "GNSS_NO_FIX" for row in context.history)


def test_transmission_failure_returns_to_data_session() -> None:
    context = run_scenario("transmission_failure")
    assert any(row["next_state"] == "DATA_SESSION" for row in context.history)


def test_retry_limit_fails() -> None:
    context = run_events([Event.TIMEOUT, Event.TIMEOUT], TrackerConfig(max_retries=1))
    assert context.history[-1]["next_state"] == "FAILED"


def test_sim_missing_can_retry_then_fail() -> None:
    context = TrackerContext(config=TrackerConfig(max_retries=0))
    assert transition(TrackerState.SIM_CHECK, Event.SIM_MISSING, context) == TrackerState.FAILED


def test_backoff_caps_value() -> None:
    assert backoff_seconds(0) == 0
    assert backoff_seconds(3, base=2) == 8
    assert backoff_seconds(10, base=2, cap=60) == 60


def test_unknown_scenario_error() -> None:
    with pytest.raises(ValueError, match="Unknown scenario"):
        run_scenario("not_real")

