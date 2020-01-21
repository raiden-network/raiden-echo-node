import logging
from sys import exit

from click import Choice, command, option

from logic import logic_choices
from raiden_bot import RequestFailed, create_raiden_bot


@command()
@option(
    "--raiden-url", default="http://127.0.0.1:5001", help="URL of the raiden node to use"
)
@option(
     "--logic", default="echo", type=Choice(logic_choices), help="Logic the bot will implement"
)
def main(raiden_url, logic):
    """
    Run a bot on top of a Raiden node. It polls the Raiden node for incoming
    payments and reacts in the way specified with the --logic option.

    Currently the only available behavior setting is 'echo', turning the Raiden
    node into an echo node (see Raiden docs for further information).
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    try:
        create_raiden_bot(raiden_url, logic).loop()
    except (RequestFailed, RuntimeError) as error:
        logging.fatal(f"Aborting due to error: {str(error)}")
        exit(f"Aborting: {str(error)}")


if __name__ == "__main__":
    main()
