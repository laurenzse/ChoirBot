FROM alpine
LABEL maintainer="LaurenzSeidel@yahoo.de"

RUN apk --update --no-cache add \
      python3 \
      ca-certificates \
      openssl

RUN pip3 install --upgrade pip \
    && pip install \
      python-telegram-bot \
      bidict \
      jsonpickle

COPY src /var/local/choirbot
WORKDIR  /var/local/choirbot

ENTRYPOINT ["/var/local/choirbot/docker-entrypoint.sh"]

CMD [ "/usr/bin/python3", "telebot.py" ]
