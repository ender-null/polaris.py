FROM ghcr.io/ender-null/polaris-base:latest as builder

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip3 install --ignore-installed -r requirements.txt

LABEL org.opencontainers.image.source https://github.com/ender-null/polaris.py

COPY . .

CMD [ "python3", "-B", "./loader.py" ]
