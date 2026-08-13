import json

from cellular_gnss_tracker_lab import cli
from cellular_gnss_tracker_lab.logs import analyze_events, parse_log_file, parse_log_line, write_synthetic_log
from cellular_gnss_tracker_lab.state_machine import run_scenario


def test_log_roundtrip_and_analysis(tmp_path) -> None:
    context = run_scenario("network_failure")
    path = write_synthetic_log(tmp_path / "network.jsonl", context.history)
    events = parse_log_file(path)
    analysis = analyze_events(events)
    assert analysis["event_count"] == len(context.history)
    assert "NETWORK_LOSS" in analysis["failures"]
    assert analysis["recovered"] is True


def test_parse_log_line_defaults_detail() -> None:
    event = parse_log_line('{"timestamp":"2026-08-13T00:00:00Z","state":"BOOT","event":"OK"}')
    assert event.detail == ""


def test_cli_simulate_and_analyze(tmp_path, capsys) -> None:
    log_path = tmp_path / "recovery.jsonl"
    assert cli.main(["simulate", "--scenario", "recovery", "--log", str(log_path)]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["scenario"] == "recovery"
    assert log_path.exists()

    assert cli.main(["analyze-log", str(log_path)]) == 0
    analysis = json.loads(capsys.readouterr().out)
    assert analysis["failures"]


def test_cli_lists_scenarios(capsys) -> None:
    assert cli.main(["list-scenarios"]) == 0
    assert "normal_operation" in capsys.readouterr().out

