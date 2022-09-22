FROM python:alpine

WORKDIR /srv/flask

COPY requirements.txt ./
RUN apk add musl-dev
RUN apk add g++
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "server", "start"]
