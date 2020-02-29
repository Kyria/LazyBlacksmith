#!/bin/bash

# copy the default docker config if none exist / have been mounted
if [[ ! -r "/lb/config.py" ]]
then
    cp -f /lb/config.docker /lb/config.py
fi

source /venv/bin/activate
if [[ "$SKIP_CLI" -ne 1 ]]
then
    python manage.py db upgrade
    python manage.py sde_import -d
fi

uwsgi -p $UWSGI_PROCESSES $UWSGI_SOCKET_TYPE :9090 --chdir /lb --home /venv --module app:APP --master