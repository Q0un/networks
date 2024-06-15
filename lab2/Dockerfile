FROM ubuntu:22.04

WORKDIR /usr/src/app
RUN apt update && apt install -y python3 iputils-ping

COPY ./main.py .
