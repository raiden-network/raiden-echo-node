import logging
from itertools import count
from json import JSONDecodeError, loads
from requests import get
from requests.exceptions import RequestException
from time import sleep

from logic import Payment, get_logic


def request(endpoint, field=None):
    try:
        response = get(endpoint)
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

    def get_payments(self):
        payments = []
        for token in self.tokens:
            payment_records = request(self.url + f"/api/v1/payments/{token}/{self.address}")
            payments.extend(parse_received_payments(payment_records))
        return payments


class RaidenBot:
    def __init__(self, endpoint, logic, poll_interval=1.0):
        self.endpoint = endpoint
        self.logic = logic
        self.poll_interval = poll_interval

    def loop(self):
        while True:
            payments_in = self.endpoint.get_payments()
            payments_out = self.logic.handle_payments(payments_in)

            if payments_in or payments_out:
                logging.info(f"Received {len(payments_in)} transfers.")
                logging.info(f"Issuing {len(payments_out)} new transfers.")

            for transfer in payments_out:
                self.endpoint.transfer(transfer)

            sleep(self.poll_interval)


def create_raiden_bot(raiden_url, logic_class):
    endpoint = RaidenEndpoint(url=raiden_url)
    logic = get_logic(logic_class, endpoint.address)
    bot = RaidenBot(endpoint, logic)

    logging.info(f"Bot successfully created with raiden url {raiden_url}.")

    return bot
