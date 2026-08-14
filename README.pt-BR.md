# Cellular GNSS Tracker Lab

Laboratorio publico de engenharia para rastreador ESP32 com modem celular, GNSS, maquina de estados, recuperacao de falhas e ferramentas Python.

## Por que existe

Rastreadores celulares falham em pontos diferentes: modem sem resposta, SIM ausente, registro de rede negado, sessao de dados instavel, GNSS sem fix, falha de transmissao e recuperacao apos timeout. Este projeto modela esses cenarios de forma publica, sintetica e reproduzivel.

## O que demonstra

- Maquina de estados para ciclo de rastreador.
- Parser generico de respostas AT.
- Parser de posicao GNSS sintetica.
- Retries, watchdog, reset de modem e limite de recuperacao.
- Logs JSONL sinteticos.
- CLI Python para simular e analisar logs.
- Firmware skeleton publico para ESP32.

## Validado

- Software.
- Parser AT/GNSS.
- Maquina de estados.
- Logs sinteticos.
- Testes automatizados.
- CI, CodeQL e dependency review.

## Ainda nao validado

- Modem real.
- SIM real.
- Antenas reais.
- GNSS fisico.
- Rede celular real.
- Transmissao contra servidor real.

## Como demonstrar sem hardware

```bash
python -m pip install -e ".[dev]"
cellular-gnss-lab simulate --scenario recovery --log reports/recovery.jsonl
cellular-gnss-lab analyze-log reports/recovery.jsonl
```

## Validacao fisica futura

Veja:

- [docs/hardware-validation.md](docs/hardware-validation.md)
- [docs/at-command-flow.md](docs/at-command-flow.md)
- [docs/state-machine.md](docs/state-machine.md)

