# Running with docker

## Requirements

By default (with the default configuration) this containers requires the following container or services to be available:
- database (default link name: db): either mysql/mariadb or postgresql
- rabbitmq (default link name: rabbitmq): rabbitmq or any similar messaging queue

You can also use redis or whatever you want, but you will have to adjust the configuration / environment variables.

## Available volume

The container provide a specific volume `/static` which will contain the static files. <br>
If you use nginx or any webserver to serve static file, do not hesitate to map it !

## Environment variables

| Variable | Defaults | Description |
|-|-|-|
| SECRET_KEY            | "YouNeedToChangeThis8946513!!??" | The secret key used for persistent session in flask. Please set your own ! |
| DB_URI                | "mysql://user:password@db/db" | The DB URI to connect to the database |
| EVE_DATASOURCE        | "tranquility" | ESI Related configuration: define where you get resources (tranquility, singularity...)|
| ESI_SECRET_KEY        | "" | ESI Secret Key from https://developers.eveonline.com/ |
| ESI_CLIENT_ID         | "" | ESI Client ID from https://developers.eveonline.com/  |
| ESI_REDIRECT_DOMAIN   | "" | Redirect Base domain for ESI callback. This must be the root of your Lazyblacksmith instance, for example "http://127.0.0.1:9090 from this container |
| ESI_USER_AGENT        | "LazyBlacksmith Docker/1.0" | Define the user agent that will be send with ESI queries. Use something that means really something / A way to contact you |
| MARKET_ORDER_THREADS  | 4 | Number of threads used to gather regions market orders. The more you have the faster it may be, but also the more memory you will use |
| EVE_TYPES_URL         | http://content.eveonline.com/data/Invasion_1.0_Types.zip | The URL to get the expansion types from https://developers.eveonline.com/resource/resources |
| UWSGI_PROCESSES       | 4 | The number of uwsgi worker to run the application. |
| UWSGI_SOCKET_TYPE     | "--socket" | Use "--socket" (default) to use this container behind a nginx instance (with uwsgi_pass). Use "--http-socket" to use http proxy (other than nginx) or direct access to this container |
| UWSGI_OPTIONS         | "" | Use this to give uwsgi any other options you may need |
| CELERY_BROKER         | "amqp://guest:guest@rabbitmq:5672" | The broker URI to connect the messaging queue for Celery |
| CELERY_RESULT_BACKEND | "rpc://" | The result backend URI for celery |
| CELERY_CONCURRENCY    | 4 | The number of worker run by celery |
| CELERY_LOGLEVEL       | INFO | Default log verbosity |
| CELERY_OPTIONS        | "" | Any options you may want to provide to celery workers and/or celery beat. |

You may also want to provide your own `config.py` file if you need more customization (caching, market order region...).
In this case just map the file to the container with `-v /your/custom/config.py:/lb/config.py`

You can find [the default configurations here](https://github.com/Kyria/LazyBlacksmith/blob/master/config.dist)

## Start the application

The image allows you to run 3 different type of process:

* `uwsgi` (the default): this will start uwsgi within the container and serve the python app. **This will also update the SDE and database each time you run it, unless you provide a second argument (different from "0") to avoid this**
* `celery`: this will start the celery workers
* `celery-beat`: this will start the celery scheduler to schedule the tasks

To run the application simply run the container (default config):

```bash
# run uwsgi
SKIP_DB_UPGRADE=0 # set it to 1 if you don't want to upgrade database at runtime
docker run -it --name lazyblacksmith -p 9090:9090 -e UWSGI_SOCKET_TYPE="--http-socket" \
        --link rabbitmq --link db \
        -e ESI_SECRET_KEY=secretkey -e ESI_CLIENT_ID=clientid -e ESI_REDIRECT_DOMAIN="http://container_or_serverIP_or_dns:9090" \
        -e DB_URI='mysql://user:password@db/lazyblacksmith' \
        anakhon/lazyblacksmith uwsgi $SKIP_DB_UPGRADE

# run celery
docker run -it --name lazyblacksmith-celery \
        --link rabbitmq --link db \
        -e ESI_SECRET_KEY=secretkey -e ESI_CLIENT_ID=clientid \
        -e DB_URI='mysql://user:password@db/lazyblacksmith' \
        anakhon/lazyblacksmith celery

# run celery beat
docker run -it --name lazyblacksmith-celerybeat \
        --link rabbitmq --link db \
        anakhon/lazyblacksmith celery-beat
```

## Upgrade elements in the container

If you need to upgrade something in the container you can use the `docker exec` command, like the following:

**prerequisite:** "lazyblacksmith" container should run !

```bash
docker exec -it lazyblacksmith <command>
```

Where command can be one of the following.

| Command | Description |
|-|-|
| `dl_eve_types http://someURL` | Download the files from the URL provided. This is to update the EVE Types images from https://developers.eveonline.com/resource/resources |
| `update_static_files` | Update the static files in the volume `/static`. This is required after an upgrade ! |
| `bash -c "source /venv/bin/activate && python manage.py db upgrade"` | Upgrade the database model (required if you use SKIP_DB_UPGRADE from above) |
| `bash -c "source /venv/bin/activate && python manage.py sde_import -d"` | Upgrade the sde data by downloading the latest export from fuzzwork (required if you use SKIP_DB_UPGRADE from above) |
| `bash -c "source /venv/bin/activate && python celery_cli.py tasks -u"` | Manually run the celery tasks to update universe data |
| `bash -c "source /venv/bin/activate && python celery_cli.py tasks -c"` | Manually run the celery tasks to update character data |
| `bash -c "source /venv/bin/activate && python celery_cli.py tasks -p"` | Manually run the celery tasks to purge old data |