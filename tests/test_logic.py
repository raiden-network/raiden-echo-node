from dataclasses import replace

import pytest

from logic import EchoLogic, Payment


@pytest.fixture
def echo_logic():
    return EchoLogic(our_address="0x000000000000000000000000000000000000ec50")


def make_address(i):
    return f"0x{i:040x}"


def test_echo_logic_amount_multiple_of_three(echo_logic):
    address = make_address(1)
    token = make_address(1000)
    payment = Payment(sender=address, recipient=echo_logic.our_address, amount=0, token=token)
    assert not echo_logic.handle_payment(payment)
    assert not echo_logic.handle_payment(replace(payment, amount=4))
    assert not echo_logic.handle_payment(replace(payment, recipient=make_address(2)))

    echo_payments = echo_logic.handle_payment(replace(payment, amount=9))
    assert echo_payments
    echo_payment = echo_payments[0]
    assert echo_payment.amount == 8
    assert echo_payment.sender == echo_logic.our_address
    assert echo_payment.recipient == address
