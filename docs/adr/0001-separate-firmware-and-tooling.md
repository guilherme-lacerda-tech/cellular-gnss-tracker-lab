# ADR 0001: Separate Firmware and Python Tooling

## Status

Accepted.

## Context

An embedded tracker lab needs firmware concepts, but public CI cannot depend on a specific ESP32 board, modem, SIM, GNSS antenna or cellular network.

## Decision

The repository separates firmware examples from Python simulation and analysis tooling. The Python tooling is the validated path for CI and public demos.

## Consequences

- The project remains useful without hardware.
- The firmware can document architecture without pretending to be physically validated.
- Future hardware validation can be added without rewriting the simulation layer.

