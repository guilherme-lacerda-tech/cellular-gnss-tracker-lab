# Architecture

```mermaid
flowchart TD
    Firmware["ESP32 firmware skeleton"] --> Modem["Generic cellular modem"]
    Modem --> GNSS["GNSS"]
    Modem --> Network["Cellular network"]
    Network --> MockServer["Mock telemetry endpoint"]
    Simulator["Python simulator"] --> StateMachine["Tracker state machine"]
    Logs["Synthetic JSONL logs"] --> Analyzer["Python log analyzer"]
```

The Python model mirrors the public state-machine concepts used by the firmware skeleton. It provides deterministic validation for retries, recovery and failure classification while hardware validation remains pending.

