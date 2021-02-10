FROM tiangolo/uwsgi-nginx-flask:python3.8

MAINTAINER zzzmahesh@gmail.com

ENV LISTEN_PORT 8080

COPY requirements.txt /app/

RUN cd /app \
    && pip3 install -r requirements.txt

COPY main.py /app/

EXPOSE 8080