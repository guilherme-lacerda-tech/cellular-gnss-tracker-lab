# Maquina de Estados / State Machine

## Diagrama

```mermaid
stateDiagram-v2
    [*] --> BOOT
    BOOT --> MODEM_INIT
    MODEM_INIT --> SIM_CHECK
    SIM_CHECK --> NETWORK_REGISTRATION
    NETWORK_REGISTRATION --> DATA_SESSION
    DATA_SESSION --> GNSS
    GNSS --> POSITION
    POSITION --> TRANSMISSION
    TRANSMISSION --> SLEEP_WAIT
    SLEEP_WAIT --> MODEM_INIT
    MODEM_INIT --> RECOVERY: timeout
    NETWORK_REGISTRATION --> RECOVERY: network loss / denied
    DATA_SESSION --> RECOVERY: session failure
    GNSS --> GNSS: no fix
    POSITION --> GNSS: bad position
    TRANSMISSION --> DATA_SESSION: transmission failure
    RECOVERY --> MODEM_INIT
    RECOVERY --> FAILED: retry limit
```

## Validado por software

- Transicao normal ate `SLEEP_WAIT`.
- Timeout de modem.
- Perda de rede.
- GNSS sem fix.
- Falha de transmissao.
- Limite de recuperacao.
- Logs sinteticos JSONL.

## Ainda nao validado em hardware

- Comportamento real de modem.
- Tempo real de registro.
- Tempo real de fix GNSS.
- Consumo em sleep/wait.
- Recuperacao apos perda fisica de sinal.

## English Summary

The state machine is validated through deterministic Python tests and synthetic logs. Real modem/GNSS timing remains hardware-validation work.

