# Raiden Echo node

This is a testing tool for the [Raiden
network](https://github.com/raiden-network/raiden). It enables users who
want to try out Raiden to send transfers to a node operated by a bot
with a fixed set of automatic responses.

Details can be found in the [docs of the main
project](https://raiden-network.readthedocs.io). The bot will act as an
echo node for all registered tokens on the given network.

If you want to write a bot on top of a Raiden node with different
behavior than the echo node, cloning this repo will also be a good
starting point.

## Running the Docker setup

In order to run the docker-compose setup, please specify the Ethereum
node, network and account in the `raiden/` directory:

  - Copy the keystore file of the account you want to run the echo node
    on there
  - Save the password of the account there, in a file named `password`
  - Create a `config.toml` from the `config-template.toml` and fill
    in the account's address, the network id and the url of the node.
