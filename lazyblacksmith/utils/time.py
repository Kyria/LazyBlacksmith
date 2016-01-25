# -*- encoding: utf-8 -*-
import pytz

from datetime import datetime


def utcnow():
    utc_now = datetime.utcnow()
    utc_now = utc_now.replace(tzinfo=pytz.utc)
    return utc_now
