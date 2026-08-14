# Validacao de Hardware / Hardware Validation

Este documento prepara uma validacao fisica futura. A release atual nao afirma validacao com modem real, SIM real, rede real ou GNSS fisico.

## Hardware necessario

- ESP32 compativel.
- Modem celular/GNSS compativel com comandos AT publicos.
- Fonte adequada para picos de corrente do modem.
- SIM de teste autorizado para uso pessoal/lab.
- Antena celular.
- Antena GNSS.
- Fios UART curtos e bem identificados.
- Conversor USB/serial para debug, se necessario.

## Configuracao segura

Use somente exemplos publicos:

```cpp
static constexpr const char* CELLULAR_APN = "example.apn";
static constexpr const char* TELEMETRY_HOST = "example.invalid";
static constexpr int TELEMETRY_PORT = 1883;
```

Nunca publique APN real, servidor real, IMEI, ICCID, numero de telefone, localizacao real, logs privados ou dados de cliente.

## Conexoes esperadas

- ESP32 TX -> modem RX.
- ESP32 RX -> modem TX.
- GND comum.
- Alimentacao do modem dimensionada conforme datasheet publico.
- Antenas conectadas antes de energizar, quando o fabricante exigir.

## Fluxo de validacao

1. Energizar ESP32 e modem.
2. Confirmar boot no serial monitor.
3. Enviar/observar `AT`.
4. Confirmar SIM com comando publico apropriado.
5. Confirmar registro de rede.
6. Abrir sessao de dados com configuracao de exemplo local.
7. Habilitar GNSS.
8. Aguardar fix em area aberta.
9. Capturar posicao sintetica ou anonima para teste privado.
10. Simular transmissao contra endpoint local/mock, nao servidor real de empresa.
11. Forcar perda de rede e observar recuperacao.
12. Forcar cenario sem fix e observar retry/timeout.

## Logs esperados

Estados esperados:

- `BOOT`
- `MODEM_INIT`
- `SIM_CHECK`
- `NETWORK_REGISTRATION`
- `DATA_SESSION`
- `GNSS`
- `POSITION`
- `TRANSMISSION`
- `SLEEP_WAIT`
- `RECOVERY`

## Checklist fisico

- [ ] modem responde AT
- [ ] SIM detectado
- [ ] network registered
- [ ] data session active
- [ ] GNSS enabled
- [ ] GNSS fix acquired
- [ ] position parsed
- [ ] transmission simulation completed
- [ ] network recovery works
- [ ] no-fix recovery works

## Evidencia aceitavel

Pode ser guardado localmente:

- log serial sem IMEI/ICCID;
- tempo ate registro;
- tempo ate fix;
- estado final;
- contadores de retry/reset.

Nao publicar logs brutos sem revisao manual.

## English Summary

The project is currently simulation/software validated. Physical validation should use a generic ESP32 plus a public AT-command cellular/GNSS modem, example APN/host values and no private identifiers.

