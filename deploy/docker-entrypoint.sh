#!/bin/bash
source /venv/bin/activate

# check parameters
export ACTION=$1
export SKIP=${2:-0}

# copy the default docker config if none exist / have been mounted
if [[ ! -r "/lb/config.py" ]]
then
    cp -f /lb/config.docker /lb/config.py
fi

function run_sde_import {
    python manage.py sde_import -d -n /sde/sqlite-latest.sqlite
}

function run_init_db {
    # check if we want to skip the db upgrade at startup
    if [[ "$SKIP" -eq 0 ]]
    then
        python manage.py db upgrade
        if [[ ! -e /sde/sqlite-latest.sqlite ]]
        then
            run_sde_import
        fi
    fi
}

function run_uwsgi {
    # starting uwsgi, define options and run
    SOCKET_PORT="$UWSGI_SOCKET_TYPE :9090"
    exec uwsgi -p $UWSGI_PROCESSES $SOCKET_PORT \
               --chdir /lb --home /venv \
               --module app:APP \
               --hook-master-start "unix_signal:15 gracefully_kill_them_all" \
               --master \
               $UWSGI_OPTIONS
}

function run_celery {
    exec celery -A app_celery:celery_app worker -c $CELERY_CONCURRENCY --loglevel $CELERY_LOGLEVEL $CELERY_OPTIONS
}

function run_celery_beat {
    exec celery -A app_celery:celery_app beat $CELERY_OPTIONS
}

case $ACTION in
    'uwsgi') run_uwsgi;;
    'celery') run_celery;;
    'celery-beat') run_celery_beat;;
    'init-db') run_init_db;;
    'sde-import') run_sde_import;;
    *) exec "$@";;
esac
