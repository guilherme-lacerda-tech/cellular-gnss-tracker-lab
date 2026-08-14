from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TrackerState(str, Enum):
    BOOT = "BOOT"
    MODEM_INIT = "MODEM_INIT"
    SIM_CHECK = "SIM_CHECK"
    NETWORK_REGISTRATION = "NETWORK_REGISTRATION"
    DATA_SESSION = "DATA_SESSION"
    GNSS = "GNSS"
    POSITION = "POSITION"
    TRANSMISSION = "TRANSMISSION"
    SLEEP_WAIT = "SLEEP_WAIT"
    RECOVERY = "RECOVERY"
    FAILED = "FAILED"


class Event(str, Enum):
    OK = "OK"
    TIMEOUT = "TIMEOUT"
    SIM_MISSING = "SIM_MISSING"
    REGISTRATION_DENIED = "REGISTRATION_DENIED"
    NETWORK_LOSS = "NETWORK_LOSS"
    GNSS_NO_FIX = "GNSS_NO_FIX"
    TRANSMISSION_FAILURE = "TRANSMISSION_FAILURE"


@dataclass(frozen=True)
class TrackerConfig:
    max_retries: int = 3
    base_backoff_seconds: int = 2
    apn: str = "example.apn"
    server: str = "example.invalid"
    port: int = 1883


@dataclass
class TrackerContext:
    config: TrackerConfig = field(default_factory=TrackerConfig)
    retries: int = 0
    modem_resets: int = 0
    watchdog_kicks: int = 0
    transmissions: int = 0
    last_position: tuple[float, float] | None = None
    history: list[dict[str, object]] = field(default_factory=list)

    def record(self, state: TrackerState, event: Event, next_state: TrackerState, detail: str) -> None:
        self.history.append(
            {
                "state": state.value,
                "event": event.value,
                "next_state": next_state.value,
                "retries": self.retries,
                "detail": detail,
            }
        )


NEXT_ON_OK: dict[TrackerState, TrackerState] = {
    TrackerState.BOOT: TrackerState.MODEM_INIT,
    TrackerState.MODEM_INIT: TrackerState.SIM_CHECK,
    TrackerState.SIM_CHECK: TrackerState.NETWORK_REGISTRATION,
    TrackerState.NETWORK_REGISTRATION: TrackerState.DATA_SESSION,
    TrackerState.DATA_SESSION: TrackerState.GNSS,
    TrackerState.GNSS: TrackerState.POSITION,
    TrackerState.POSITION: TrackerState.TRANSMISSION,
    TrackerState.TRANSMISSION: TrackerState.SLEEP_WAIT,
}


def backoff_seconds(retries: int, base: int = 2, cap: int = 60) -> int:
    if retries <= 0:
        return 0
    return min(cap, base * (2 ** (retries - 1)))


def transition(state: TrackerState, event: Event, context: TrackerContext) -> TrackerState:
    if event == Event.OK:
        if state == TrackerState.POSITION:
            context.last_position = (-23.5505, -46.6333)
        if state == TrackerState.TRANSMISSION:
            context.transmissions += 1
        if state == TrackerState.SLEEP_WAIT:
            return TrackerState.MODEM_INIT
        context.retries = 0
        return NEXT_ON_OK.get(state, TrackerState.SLEEP_WAIT)

    if event in {
        Event.TIMEOUT,
        Event.REGISTRATION_DENIED,
        Event.NETWORK_LOSS,
        Event.GNSS_NO_FIX,
        Event.TRANSMISSION_FAILURE,
    }:
        context.retries += 1
        context.watchdog_kicks += 1
        if event in {Event.TIMEOUT, Event.REGISTRATION_DENIED, Event.NETWORK_LOSS}:
            context.modem_resets += 1
        if context.retries > context.config.max_retries:
            return TrackerState.FAILED
        if event == Event.GNSS_NO_FIX:
            return TrackerState.GNSS
        if event == Event.TRANSMISSION_FAILURE:
            return TrackerState.DATA_SESSION
        return TrackerState.RECOVERY

    if event == Event.SIM_MISSING:
        context.retries += 1
        return TrackerState.FAILED if context.retries > context.config.max_retries else TrackerState.SIM_CHECK

    return TrackerState.FAILED


def run_events(events: list[Event], config: TrackerConfig | None = None) -> TrackerContext:
    context = TrackerContext(config=config or TrackerConfig())
    state = TrackerState.BOOT
    for event in events:
        next_state = transition(state, event, context)
        detail = f"{state.value} received {event.value}"
        context.record(state, event, next_state, detail)
        if next_state == TrackerState.RECOVERY:
            state = TrackerState.MODEM_INIT
        else:
            state = next_state
        if state == TrackerState.FAILED:
            break
    return context


SCENARIO_EVENTS: dict[str, list[Event]] = {
    "normal_operation": [Event.OK] * 8,
    "network_failure": [
        Event.OK,
        Event.OK,
        Event.OK,
        Event.NETWORK_LOSS,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
    ],
    "registration_denied": [
        Event.OK,
        Event.OK,
        Event.OK,
        Event.REGISTRATION_DENIED,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
    ],
    "gnss_no_fix": [Event.OK, Event.OK, Event.OK, Event.OK, Event.OK, Event.GNSS_NO_FIX, Event.OK, Event.OK, Event.OK],
    "modem_timeout": [Event.OK, Event.TIMEOUT, Event.OK, Event.OK, Event.OK, Event.OK, Event.OK, Event.OK, Event.OK],
    "transmission_failure": [
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.TRANSMISSION_FAILURE,
        Event.OK,
        Event.OK,
        Event.OK,
    ],
    "recovery": [
        Event.OK,
        Event.TIMEOUT,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.NETWORK_LOSS,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
        Event.OK,
    ],
}


def run_scenario(name: str, config: TrackerConfig | None = None) -> TrackerContext:
    try:
        events = SCENARIO_EVENTS[name]
    except KeyError as exc:
        valid = ", ".join(sorted(SCENARIO_EVENTS))
        raise ValueError(f"Unknown scenario '{name}'. Valid scenarios: {valid}") from exc
    return run_events(events, config)


def scenario_names() -> list[str]:
    return sorted(SCENARIO_EVENTS)
