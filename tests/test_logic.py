from dataclasses import replace

import pytest

from logic import EchoLogic, Transfer


@pytest.fixture
def echo_logic():
    return EchoLogic(our_address="0x000000000000000000000000000000000000ec50")


def make_address(i):
    return f"0x{i:040x}"


def test_echo_logic_amount_multiple_of_three(echo_logic):
    address = make_address(1)
    transfer = Transfer(sender=address, recipient=echo_logic.our_address, amount=0)
    assert not echo_logic.handle_transfer(transfer)
    assert not echo_logic.handle_transfer(replace(transfer, amount=4))
    assert not echo_logic.handle_transfer(replace(transfer, recipient=make_address(2)))

    echo_transfers = echo_logic.handle_transfer(replace(transfer, amount=9))
    assert echo_transfers
    echo_transfer = echo_transfers[0]
    assert echo_transfer.amount == 8
    assert echo_transfer.sender == echo_logic.our_address
    assert echo_transfer.recipient == address
            
