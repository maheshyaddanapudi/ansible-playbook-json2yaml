FROM tiangolo/uwsgi-nginx-flask:python3.8

MAINTAINER zzzmahesh@gmail.com

ENV PORT 5000

ENV LISTEN_PORT \$PORT

COPY requirements.txt /app/

RUN cd /app \
    && pip3 install -r requirements.txt

COPY main.py /app/

EXPOSE $PORT
