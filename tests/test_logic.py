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
