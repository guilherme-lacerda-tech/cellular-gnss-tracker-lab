# Contributing

Keep this lab independent, synthetic and hardware-optional.

## Local Validation

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest --cov --cov-report=term-missing -q
```

## Data Rules

Never add real APNs, endpoints, IMEI, ICCID, customer positions, internal logs, private firmware or proprietary command sequences.

