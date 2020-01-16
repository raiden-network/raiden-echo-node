from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Payment:
    token: str
    amount: int
    sender: Optional[str] = None
    recipient: Optional[str] = None


class EchoLogic:
    """
    Logic class defining the Raiden echo node:

    - Every received payment will be echoed with a payment of the same amount,
      unless the amount is 7 or a multiple of 3.
    - If the amount is a multiple of 3, the amount of the echo payment is one
      less than the sent amount.
    - If the amount is equal to 7, the sender enters the 'lottery'.
      They will not receive a payment in return, unless they are the seventh
      participant entering the lottery, in which case they receive an amount
      of 49.
    - If the amount is equal to 7 and the sender is already in the lottery,
      they will receive a payment with the amount equal to the current number
      of lottery participants.
    """
    def __init__(self):
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


def get_logic(name):
    if name not in _logic_classes:
        raise RuntimeError("Unknown logic")
    return _logic_classes[name]()
