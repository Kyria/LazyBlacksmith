# -*- encoding: utf-8 -*-
from . import db

from lazyblacksmith.models.utcdatetime import UTCDateTime

from sqlalchemy import func


class TaskStatus(db.Model):
    name = db.Column(db.String(250), primary_key=True)
    expire = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    last_run = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    results = db.Column(db.Text())