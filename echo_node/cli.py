from sys import exit

import click

from raiden_bot import make_raiden_endpoint


@click.command()
@click.option(
    "--raiden-url", default="http://127.0.0.1:5001", help="URL of the raiden node to use"
)
def main(raiden_url):
    try:
        endpoint = make_raiden_endpoint(raiden_url)
    except RuntimeError as error:
        exit(str(error))


if __name__ == "__main__":
    main()

