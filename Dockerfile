
FROM python:3.7
# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
# Install linux dependencies
RUN apt-get update && apt-get install -y libssl-dev
RUN apt-get update && apt-get install -y npm
# Install brownie deps
RUN npm install -g ganache-cli
COPY . ../brownie-config.yaml .
RUN rm -rf build/*
RUN pip install -r requirements.txt
RUN brownie compile
RUN brownie test