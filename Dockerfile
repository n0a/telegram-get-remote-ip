# Dockerfile
FROM ubuntu:20.04

# Installing git and python3 pip
RUN apt update && apt install -yq python3-pip git
# Installing tshark
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tshark
# Cloning repository and moving into it
RUN git clone https://github.com/n0a/telegram-get-remote-ip
COPY ./tg_get_ip.py ./telegram-get-remote-ip
# Installing dependencies
RUN cd telegram-get-remote-ip && python3 -m pip install -r requirements.txt
# Seting WORKDIR
WORKDIR /telegram-get-remote-ip