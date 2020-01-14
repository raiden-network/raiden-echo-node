import logging
from json import JSONDecodeError, loads
from requests import get
from requests.exceptions import RequestException
from time import sleep

from logic import Transfer, get_logic


def get_content(response):
    try:
        return loads(response.content)
    except JSONDecodeError:
        raise RuntimeError("Cannot parse response Invalid JSON")


class RaidenEndpoint:
    def __init__(self, url):
        self.url = url

    def get_address(self):
        try:
            response = get(self.url + "/api/v1/address")
        except RequestException as exception:
            raise RuntimeError(
                f"Couldn't connect to raiden node at {raiden_url}."
                f"\n\nRequest failed with: {str(exception)}"
            )
        try:
            return get_content(response)["our_address"]
        except KeyError:
            raise RuntimeError("Invalid answer from address query (no field named our_address)")

    def get_transfers(self):
        return []


class RaidenBot:
    def __init__(self, endpoint, logic, poll_interval=1.0):
        self.endpoint = endpoint
        self.logic = logic
        self.poll_interval = poll_interval

    @property
    def address(self):
        return self.logic.our_address

    def loop(self):
        while True:
            transfers_in = self.endpoint.get_transfers()
            transfers_out = self.logic.handle_transfers(transfers_in)

            if transfers_in or transfers_out:
                logging.info(f"Received {len(transfers_in)} transfers.")
                logging.info(f"Issuing {len(transfers_out)} new transfers.")

            for transfer in transfers_out:
                self.endpoint.transfer(transfer)

            sleep(self.poll_interval)



def create_raiden_bot(raiden_url, logic_class):
    endpoint = RaidenEndpoint(url=raiden_url)
    logic = get_logic(logic_class, endpoint.get_address())
    bot = RaidenBot(endpoint, logic)

    logging.info(f"Bot successfully created with raiden url {raiden_url}.")
    logging.info(f"Found raiden address: {bot.address}")

    return bot
