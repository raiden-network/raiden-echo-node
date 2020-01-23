import logging
from sys import exit
from time import sleep

from click import Choice, IntRange, command, option

from logic import logic_choices
from raiden_bot import RequestFailed, create_raiden_bot


def start_bot(url, logic, timeout):
    if timeout > 0:
        logging.info(f"Trying to connect to Raiden node at {url}. Timeout: {timeout} seconds")
    fail_reason = None
    while timeout >= 0:
        try:
            return create_raiden_bot(url, logic)
        except (RequestFailed, RuntimeError) as e:
            fail_reason = str(e)
        sleep(min(timeout, 5.0))
        timeout -= 5
    else:
        logging.fatal(f"Failed to connect to Raiden node at {url}: {fail_reason}")
        exit("Aborting")


@command()
@option(
    "--raiden-url", default="http://127.0.0.1:5001", help="URL of the Raiden node to use"
)
@option(
     "--logic", default="echo", type=Choice(logic_choices), help="Logic the bot will implement"
)
@option(
    "--timeout",
    type=IntRange(min=0),
    default=0,
    help="Seconds to wait for the Raiden API to become available before aborting."
)
def main(raiden_url, logic, timeout):
    """
    Run a bot on top of a Raiden node. It polls the Raiden node for incoming
    payments and reacts in the way specified with the --logic option.

    Currently the only available behavior setting is 'echo', turning the Raiden
    node into an echo node (see Raiden docs for further information).
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    start_bot(raiden_url, logic, timeout).loop()


if __name__ == "__main__":
    main()
