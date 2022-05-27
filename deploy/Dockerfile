FROM node:12-slim as js-builder

COPY package.json package-lock.json /lb/

WORKDIR /lb

RUN npm install

COPY . /lb/

RUN npm run dist

RUN mkdir -p /static \
    && cp -fR /lb/lazyblacksmith/static/js  /static \
    && cp -fR /lb/lazyblacksmith/static/css /static \
    && cp -fR /lb/lazyblacksmith/static/img /static

# ------------------------------------

FROM python:3.9-slim as py-builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev libmariadb-dev

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements .

RUN pip install --upgrade pip && \
    pip install -U -r global-requirements.txt && \
    pip install -U -r mysql-requirements.txt && \
    pip install -U -r postgresql-requirements.txt && \
    pip install -U uwsgi redis

# ------------------------------------

FROM python:3.9-slim AS runtime
LABEL maintainer="anakhon@gmail.com"

ENV PATH="/venv/bin:/lb/deploy:$PATH" \
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
    UWSGI_PROCESSES=4 \
    UWSGI_SOCKET_TYPE="--socket" \
    UWSGI_OPTIONS="" \
    CELERY_CONCURRENCY=4 \
    CELERY_LOGLEVEL=INFO \
    CELERY_OPTIONS=""

EXPOSE 9090

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev libmariadb-dev \
    && groupadd -g 1001 lb \
    && useradd -M -s /bin/false -u 1001 -g lb -d /lb lb

COPY --chown=lb:lb --from=py-builder /venv /venv
COPY --chown=lb:lb --from=js-builder /static /static
COPY --chown=lb:lb . /lb/

RUN chmod a+x /lb/deploy/*

VOLUME [ "/static" ]

RUN mkdir /sde && \
    chown lb:lb /sde

VOLUME [ "/sde" ]

USER lb:lb

WORKDIR /lb

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uwsgi"]
