from json import dumps, loads

import pytest
from httmock import HTTMock, all_requests
from requests import RequestException

from logic import EchoLogic, Payment
from raiden_bot import create_raiden_bot, RequestFailed, parse_received_payments


def make_address(i):
    return f"0x{i:040x}"


sample_data = """
[
    {
        "event": "EventPaymentSentFailed",
        "log_time": "2020-01-15T17:57:56.834000",
        "reason": "there is no route available",
        "target": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "event": "EventPaymentSentFailed",
        "log_time": "2020-01-15T17:58:05.887000",
        "reason": "there is no route available",
        "target": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "1",
        "event": "EventPaymentReceivedSuccess",
        "identifier": "17",
        "initiator": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "log_time": "2020-01-15T18:24:26.341000",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "3",
        "event": "EventPaymentReceivedSuccess",
        "identifier": "19",
        "initiator": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "log_time": "2020-01-15T18:27:17.663000",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "42",
        "event": "EventPaymentReceivedSuccess",
        "identifier": "22",
        "initiator": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "log_time": "2020-01-15T18:27:32.583000",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    },
    {
        "amount": "66",
        "event": "EventPaymentSentSuccess",
        "identifier": "31",
        "log_time": "2020-01-16T10:11:42.455000",
        "target": "0x61Be41317a57D1C869CDf612A4e47745b189DBde",
        "token_address": "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
    }
]
"""


partner_address = "0x61Be41317a57D1C869CDf612A4e47745b189DBde"
token_address = "0x0f114A1E9Db192502E7856309cc899952b3db1ED"
expected_payments = {
    Payment(sender=partner_address, token=token_address, amount=1),
    Payment(sender=partner_address, token=token_address, amount=3),
    Payment(sender=partner_address, token=token_address, amount=42)
}


def test_parse_received_payments():
    records = loads(sample_data)
    payments = parse_received_payments(records, token_address)
    assert set(payments) == expected_payments


def address_tokens_mock(no_address=False, no_tokens=False):
    def f(url, request):
        if "/address" in url.path:
            if no_address:
                raise RequestException()
            return dict(status_code=200, content=dumps({"our_address": make_address(8)}))
        if "/tokens" in url.path:
            if no_tokens:
                return dict(status_code=404, content=dumps({"bla": "Not found"}))
            return dict(status_code=200, content=dumps([token_address, make_address(9)]))
    return all_requests(f)


def payments_mock(raise_exception=False, server_error=False):
    def f(url, request):
        assert "/payments" in url.path
        if raise_exception:
            raise RequestException()
        elif server_error:
            return dict(status_code=500, content="Internal server error.")
        elif token_address not in url.path:
            return dict(status_code=200, content="[]")
        else:
            return dict(status_code=200, content=sample_data)
    return all_requests(f)


def test_create_raiden_bot():
    with HTTMock(address_tokens_mock(no_address=True)), pytest.raises(RequestFailed):
        create_raiden_bot("http://localhost:5001", "echo")

    with HTTMock(address_tokens_mock(no_tokens=True)), pytest.raises(RequestFailed):
        create_raiden_bot("http://localhost:5001", "echo")

    with HTTMock(address_tokens_mock()):
        raiden_bot = create_raiden_bot("http://localhost:5001", "echo")
        assert raiden_bot.endpoint.address == make_address(8)
        assert make_address(9) in raiden_bot.endpoint.tokens


def test_get_payments():
    with HTTMock(address_tokens_mock()):
        raiden_bot = create_raiden_bot("http://localhost:5001", "echo")

    with HTTMock(payments_mock(raise_exception=True)):
        payments = raiden_bot.endpoint.get_payments()
        assert not payments

    with HTTMock(payments_mock(server_error=True)):
        payments = raiden_bot.endpoint.get_payments()
        assert not payments

    with HTTMock(payments_mock()):
        payments = raiden_bot.endpoint.get_payments()
        assert set(payments) == expected_payments


@pytest.fixture
def echo_logic():
    return EchoLogic()


def test_echo_logic_amount_multiple_of_three(echo_logic):
    address = make_address(1)
    token = make_address(1000)
    payment = Payment(sender=address, token=token, amount=9)

    echo_payments = echo_logic.handle_payment(payment)
    assert echo_payments
    echo_payment = echo_payments[0]
    assert echo_payment.amount == 8
    assert echo_payment.sender is None
    assert echo_payment.recipient == address


def test_echo_logic_amount_seven(echo_logic):
    token = make_address(1000)

    payment1 = Payment(sender=make_address(1), amount=7, token=token)
    issued = echo_logic.handle_payment(payment1)
    assert not issued

    issued = echo_logic.handle_payment(payment1)
    assert issued
    assert issued[0].amount == 1
    assert issued[0].recipient == make_address(1)

    for i in range(2, 7):
        payment = Payment(sender=make_address(i), amount=7, token=token)
        issued = echo_logic.handle_payment(payment)
        assert not issued

    other_payment1 = Payment(sender=make_address(3), amount=5, token=token)
    other_payment2 = Payment(sender=make_address(12), amount=9, token=token)
    echo_logic.handle_payment(other_payment1)
    echo_logic.handle_payment(other_payment2)

    payment6 = Payment(sender=make_address(6), amount=7, token=token)
    issued = echo_logic.handle_payment(payment6)
    assert issued
    assert issued[0].amount == 6
    assert issued[0].recipient == make_address(6)

    issued = echo_logic.handle_payment(payment1)
    assert issued
    assert issued[0].amount == 6
    assert issued[0].recipient == make_address(1)

    payment = Payment(sender=make_address(7), amount=7, token=token)
    issued = echo_logic.handle_payment(payment)
    assert issued
    assert issued[0].amount == 49
    assert issued[0].recipient == make_address(7)


def test_echo_logic_misc_amount(echo_logic):
    sender = make_address(10)
    token = make_address(1000)
    for amount in (4, 8, 14, 20):
        payment = Payment(sender=sender, amount=amount, token=token)
        issued = echo_logic.handle_payment(payment)
        assert issued
        assert issued[0].amount == amount
        assert issued[0].recipient == sender
