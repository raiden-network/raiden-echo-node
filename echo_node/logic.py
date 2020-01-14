from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Transfer:
    sender: str
    recipient: str
    amount: int


class EchoLogic:
    def __init__(self, our_address):
        self.our_address = our_address

    def handle_transfer(self, transfer: Transfer) -> List[Transfer]:
        if transfer.amount > 0 and transfer.recipient == self.our_address:
            echo_amount = self._echo_amount(transfer.amount, transfer.sender)
            if echo_amount > 0:
                return [
                    Transfer(
                        sender=self.our_address,
                        recipient=transfer.sender,
                        amount=echo_amount
                    )
                ]
        return []

    def handle_transfers(self, transfers: List[Transfer]) -> List[Transfer]:
        new_transfers = list()
        for transfer in transfers:
            new_transfers.extend(self.handle_transfer(transfer))
        return new_transfers

    def _echo_amount(self, amount: int, sender: str) -> int:
        if amount % 3 == 0:
            return amount - 1
        else:
            return 0


_logic_classes = {"echo": EchoLogic}


logic_choices = _logic_classes.keys()


def get_logic(name, our_address):
    if name not in _logic_classes:
        raise RuntimeError("Unknown logic")
    return _logic_classes[name](our_address)
