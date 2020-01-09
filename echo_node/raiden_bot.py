from requests import get
from requests.exceptions import ConnectionError, MissingSchema


class RaidenEndpoint:
    def __init__(self, raiden_url, our_address):
        self.raiden_url = raiden_url
        self.our_address = our_address


def make_raiden_endpoint(raiden_url):
    try:
        response = get(raiden_url + "/api/v1/address")
        our_address = response["our_address"]
        return RaidenEndpoint(raiden_url=raiden_url, our_address=our_address)
    except (ConnectionError, KeyError, MissingSchema) as exception:
        raise RuntimeError(
            f"Couldn't connect to raiden node at {raiden_url}."
            f"\n\nRequest failed with: {str(exception)}"
        )
    else:
        return RaidenEndpoint(raiden_url=raiden_url, our_address=our_address)

