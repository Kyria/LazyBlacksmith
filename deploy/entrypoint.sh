#!/bin/bash
source /venv/bin/activate

# copy the default docker config if none exist / have been mounted
if [[ ! -r "/lb/config.py" ]]
then
    cp -f /lb/config.docker /lb/config.py
fi

# check parameters
export ACTION=$1
export SKIP=${2:-0}

function run_uwsgi {
    if [[ "$SKIP" -eq 0 ]]
    then
        python manage.py db upgrade
        python manage.py sde_import -d
    fi
    exec uwsgi -p $UWSGI_PROCESSES $UWSGI_SOCKET_TYPE :9090 --chdir /lb --home /venv --module app:APP --master $UWSGI_OPTIONS
}

function run_celery {
    exec celery worker -A app_celery:celery_app -c $CELERY_CONCURRENCY --loglevel $CELERY_LOGLEVEL $CELERY_OPTIONS
}

function run_celery_beat {
    exec celery beat -A app_celery:celery_app $CELERY_OPTIONS
}

case $ACTION in
    'uwsgi') run_uwsgi;;
    'celery') run_celery;;
    'celery-beat') run_celery_beat;;
    *) run_uwsgi;;
esac
