from cellular_gnss_tracker_lab.at_commands import (
    parse_at_response,
    parse_gnss_position,
    should_retry,
)


def test_parse_ok_response() -> None:
    response = parse_at_response("AT", "AT\r\nOK\r\n")
    assert response.ok is True
    assert should_retry(response) is False


def test_parse_error_response() -> None:
    response = parse_at_response("AT+CREG?", "+CME ERROR: 10\r\n")
    assert response.ok is False
    assert response.error == "+CME ERROR: 10"
    assert should_retry(response) is True


def test_parse_timeout_response() -> None:
    response = parse_at_response("AT+QGPSLOC?", "", timed_out=True)
    assert response.timed_out is True
    assert response.error == "timeout"


def test_parse_gnss_position() -> None:
    position = parse_gnss_position("+QGPSLOC: 120000.0,-23.5505,-46.6333,1")
    assert position == (-23.5505, -46.6333, 1)


def test_parse_missing_gnss_position() -> None:
    assert parse_gnss_position("OK") is None
    assert parse_gnss_position("+QGPSLOC: bad") is None

