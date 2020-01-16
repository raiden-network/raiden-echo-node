from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Payment:
    token: str
    amount: int
    sender: Optional[str] = None
    recipient: Optional[str] = None


class EchoLogic:
    def __init__(self, our_address):
        self.our_address = our_address
        self.lottery_participants = set()

    def handle_payment(self, payment: Payment) -> List[Payment]:
        if payment.amount > 0 and not payment.recipient:
            echo_amount = self._echo_amount(payment.amount, payment.sender)
            if echo_amount > 0:
                return [
                    Payment(recipient=payment.sender, token=payment.token, amount=echo_amount)
                ]
        return []

    def handle_payments(self, payments: List[Payment]) -> List[Payment]:
        new_payments = list()
        for payment in payments:
            new_payments.extend(self.handle_payment(payment))
        return new_payments

    def _echo_amount(self, amount: int, sender: str) -> int:
        if amount % 3 == 0:
            return amount - 1
        elif amount == 7:
            participants = len(self.lottery_participants)
            assert participants < 7
            if sender in self.lottery_participants:
                return participants
            elif participants == 6:
                self.lottery_participants.clear()
                return 49
            else:
                self.lottery_participants.add(sender)
                return 0
        else:
            return amount


_logic_classes = {"echo": EchoLogic}


logic_choices = _logic_classes.keys()


def get_logic(name, our_address):
    if name not in _logic_classes:
        raise RuntimeError("Unknown logic")
    return _logic_classes[name](our_address)
