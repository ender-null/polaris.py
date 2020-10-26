FROM ghcr.io/luksireiku/polaris-js-base as builder

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt .

RUN apk add python make gcc g++
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "-B", "./loader.py" ]
