# -*- encoding: utf-8 -*-
from . import db

from lazyblacksmith.models.utcdatetime import UTCDateTime

from sqlalchemy import func


class TaskStatus(db.Model):
    name = db.Column(db.String(250), primary_key=True)
    expire = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    last_run = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    results = db.Column(db.Text())

    TASK_ADJUSTED_PRICE = 'schedule.update_adjusted_price'
    TASK_INDUSTRY_INDEX = 'schedule.update_industry_indexes'
    TASK_CHARACTER_SKILLS = 'character_skill_update [%d]'
    TASK_MARKET_ORDER = 'esi_region_order_price [%s]'
