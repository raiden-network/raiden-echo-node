import logging
from collections import defaultdict
from itertools import count
from json import JSONDecodeError, dumps, loads
from requests import get, post
from requests.exceptions import RequestException
from time import sleep

from logic import Payment, get_logic


def request(endpoint, field=None, **kwargs):
    try:
        response = get(endpoint, params=kwargs)
    except RequestException as exception:
        raise RuntimeError(
            f"Couldn't connect to endpoint node at {endpoint}."
            f"\n\nRequest failed with: {str(exception)}"
        )

    try:
        content = loads(response.content)
    except JSONDecodeError:
        raise RuntimeError("Invalid JSON in response.")

    if field is not None and field not in content:
        raise RuntimeError("Invalid answer from query to {query} (no field named {field})")
    return content[field] if field is not None else content


def parse_received_payments(records):
    payments = []
    for record in records:
        try:
            if record["event"] == "EventPaymentReceivedSuccess":
                payments.append(Payment(
                    sender=record["initiator"],
                    token=record["token_address"],
                    amount=int(record["amount"]),
                ))
        except (KeyError, TypeError, ValueError) as error:
            logging.error(f"Could not parse payment record: {error}")
            logging.error(f"Record: {record}.")
    return payments


class RaidenEndpoint:
    def __init__(self, url):
        self.url = url
        self._tokens = None
        self._address = None
        self.identifier = count(start=1)
        self.token_to_payment_offset = defaultdict(lambda: 0)

    @property
    def address(self):
        if self._address is None:
            self._address = request(self.url + "/api/v1/address", "our_address")
            logging.info(f"Our Raiden address is {self._address}.")
        return self._address

    @property
    def tokens(self):
        if self._tokens is None:
            self._tokens = request(self.url + "/api/v1/tokens")
            logging.info(f"Found {len(self._tokens)} registered tokens on the Raiden node.")
        return self._tokens

    def _get_payment_records_for_token(self, token):
        offset = self.token_to_payment_offset[token]
        payment_records = request(self.url + f"/api/v1/payments/{token}", offset=offset)
        self.token_to_payment_offset[token] += len(payment_records)
        return payment_records

    def initialize(self):
        for token in self.tokens:
            self._get_payment_records_for_token(token)
        previous_payments = sum(self.token_to_payment_offset.values())
        logging.info(f"Initializing: skipped {previous_payments} previous payments.")

    def get_payments(self):
        payments = []
        for token in self.tokens:
            payment_records = self._get_payment_records_for_token(token)
            payments.extend(parse_received_payments(payment_records))
        return payments

    def issue_payment(self, payment):
        if payment.sender is not None and payment.sender != self.address:
            logging.error(f"Wrong sender address in issued payment: {payment.sender}.")
        try:
            payload = dumps(dict(amount=payment.amount, identifier=next(self.identifier)))
            response = post(
                self.url + f"/api/v1/payments/{payment.token}/{payment.recipient}",
                data=payload
            )
        except RequestException as exception:
            logging.error(f"Payment request failed: {str(exception)}")
        else:
            if response.status_code != 200:
                logging.error(
                    f"Payment of {payment.amount} to {payment.recipient} failed: "
                    f"{response.content} ({response.status_code})"
                )


class RaidenBot:
    def __init__(self, endpoint, logic, poll_interval=1.0):
        self.endpoint = endpoint
        self.logic = logic
        self.poll_interval = poll_interval

    def loop(self):
        self.endpoint.initialize()
        while True:
            payments_in = self.endpoint.get_payments()
            payments_out = self.logic.handle_payments(payments_in)

            if payments_in or payments_out:
                logging.info(f"Received {len(payments_in)} transfers.")
                logging.info(f"Issuing {len(payments_out)} new transfers.")

            for payment in payments_out:
                self.endpoint.issue_payment(payment)

            sleep(self.poll_interval)


def create_raiden_bot(raiden_url, logic_class):
    endpoint = RaidenEndpoint(url=raiden_url)
    logic = get_logic(logic_class)
    bot = RaidenBot(endpoint, logic)

    logging.info(f"Bot successfully created with raiden url {raiden_url}.")

    return bot
