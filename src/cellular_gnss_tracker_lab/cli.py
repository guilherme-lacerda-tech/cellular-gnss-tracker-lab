from __future__ import annotations

import argparse
import json
from pathlib import Path

from cellular_gnss_tracker_lab.logs import analyze_events, parse_log_file, write_synthetic_log
from cellular_gnss_tracker_lab.state_machine import run_scenario, scenario_names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cellular-gnss-lab",
        description="Run synthetic cellular/GNSS tracker simulations and analyze logs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scenarios = subparsers.add_parser("list-scenarios", help="List available synthetic scenarios.")
    scenarios.set_defaults(func=handle_list_scenarios)

    simulate = subparsers.add_parser("simulate", help="Run a state-machine scenario.")
    simulate.add_argument("--scenario", choices=scenario_names(), default="normal_operation")
    simulate.add_argument("--log", type=Path, help="Optional JSONL log output path.")
    simulate.set_defaults(func=handle_simulate)

    analyze = subparsers.add_parser("analyze-log", help="Analyze a synthetic tracker log.")
    analyze.add_argument("path", type=Path)
    analyze.set_defaults(func=handle_analyze)
    return parser


def handle_list_scenarios(_args: argparse.Namespace) -> int:
    for scenario in scenario_names():
        print(scenario)
    return 0


def handle_simulate(args: argparse.Namespace) -> int:
    context = run_scenario(args.scenario)
    if args.log:
        write_synthetic_log(args.log, context.history)
    print(
        json.dumps(
            {
                "scenario": args.scenario,
                "steps": len(context.history),
                "modem_resets": context.modem_resets,
                "watchdog_kicks": context.watchdog_kicks,
                "transmissions": context.transmissions,
                "last_position": context.last_position,
                "history": context.history,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def handle_analyze(args: argparse.Namespace) -> int:
    events = parse_log_file(args.path)
    print(json.dumps(analyze_events(events), indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

