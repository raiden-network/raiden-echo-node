from typing import List

from raiden_bot import Transfer


class EchoLogic:
    def __init__(self, our_address):
        self.our_address = our_address

    def handle_transfer(self, transfer: Transfer) -> List[Transfer]:
        if transfer.amount > 0 and transfer.recipient == self.our_address:
            echo_amount = self._echo_amount(transfer.amount, transfer.sender)
            if echo_amount > 0:
                return [
                    Transfer(sender=self.our_address, recipient=transfer.sender, amount=echo_amount)
                ]
        return []

    def _echo_amount(self, amount: int, sender: str) -> int:
        if amount % 3 == 0:
            return amount - 1
        else:
            return 0
