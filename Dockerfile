FROM ghcr.io/luksireiku/polaris-base:latest as builder

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-B", "./loader.py" ]
