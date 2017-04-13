# -*- encoding: utf-8 -*-
from . import db
from lazyblacksmith.models.utcdatetime import UTCDateTime

from flask import json
from sqlalchemy import func


class TaskState(db.Model):
    # possible states
    QUEUED = 'queued'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'  # didn't finished
    ERROR = 'error'  # finished with error
    UNKNOWN = 'unknown'
    STATES = [QUEUED, RUNNING, SUCCESS, FAILURE, ERROR, UNKNOWN]

    # task id will always be unique as it includes datetime
    task_id = db.Column(db.String(250), primary_key=True)

    # any id used (character, corporation, region, none)
    id = db.Column(db.BigInteger)
    scope = scope = db.Column(db.String(100))

    # other data
    state = db.Column(db.String(20), default=QUEUED)
    start_date = db.Column(UTCDateTime(timezone=True))
    end_date = db.Column(UTCDateTime(timezone=True))


