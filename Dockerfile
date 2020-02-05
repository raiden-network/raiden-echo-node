FROM python:3.7
LABEL Name="Raiden echo node" 
LABEL Maintainer="Raiden Network Team <contact@raiden.network>"
COPY . /echo-node
WORKDIR /echo-node
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "echo_node/cli.py", "--config", "config-docker.toml" ]
