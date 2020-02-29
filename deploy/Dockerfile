FROM python:3.7-slim as builder
LABEL maintainer="anakhon@gmail.com"

ARG NODEJS_SOURCE=https://deb.nodesource.com/setup_12.x

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc libpq-dev libmariadb-dev curl
RUN curl -sL $NODEJS_SOURCE | bash - && apt-get install -y nodejs

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements .
RUN pip install --upgrade pip
RUN pip3 install -U -r global-requirements.txt
RUN pip3 install -U -r mysql-requirements.txt
RUN pip3 install -U -r postgresql-requirements.txt
RUN pip3 install -U uwsgi redis

COPY lazyblacksmith /lb/lazyblacksmith/
COPY lbcmd          /lb/lbcmd/
COPY lbtasks        /lb/lbtasks/
COPY migrations     /lb/migrations/
COPY app_celery.py  /lb/
COPY app.py         /lb/
COPY celery_cli.py  /lb/
COPY config.dist    /lb/
COPY manage.py      /lb/
COPY config.docker  /lb/
COPY package.json       /lb/
COPY package-lock.json  /lb/
COPY deploy/entrypoint.sh /lb/

RUN chmod a+x /lb/entrypoint.sh

WORKDIR /lb
RUN npm install
RUN npm run dist
RUN rm -fR /lb/node_modules

# ------------------------------------
FROM python:3.7-slim AS runtime

ENV PATH="/venv/bin:$PATH" \
    SECRET_KEY="YouNeedToChangeThis8946513!!??" \
    EVE_DATASOURCE="tranquility" \
    DB_URI="mysql://user:password@db/db" \
    CELERY_BROKER="amqp://guest:guest@rabbitmq:5672" \
    CELERY_RESULT_BACKEND="rpc://" \
    ESI_SECRET_KEY="" \
    ESI_CLIENT_ID="" \
    ESI_REDIRECT_DOMAIN="" \
    ESI_USER_AGENT="LazyBlacksmith Docker/1.0" \
    MARKET_ORDER_THREADS=4 \
    EVE_TYPES=http://content.eveonline.com/data/Invasion_1.0_Types.zip \
    UWSGI_PROCESSES=4 \
    UWSGI_SOCKET_TYPE="--socket"

EXPOSE 9090

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev libmariadb-dev \
    && groupadd -g 1001 lb \
    && useradd -M -s /bin/false -u 1001 -g lb -d /lb lb

COPY --chown=lb:lb --from=builder /venv /venv
COPY --chown=lb:lb --from=builder /lb /lb

USER lb:lb

WORKDIR /lb
CMD ["/lb/entrypoint.sh"]