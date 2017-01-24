# -*- encoding: utf-8 -*-
from . import db
from lazyblacksmith.models.utcdatetime import UTCDateTime

from sqlalchemy import func
from flask import json


class TaskStatus(db.Model):
    name = db.Column(db.String(250), primary_key=True)
    expire = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    last_run = db.Column(UTCDateTime(timezone=True), server_default=func.now())
    results = db.Column(db.Text())

    TASK_ADJUSTED_PRICE = 'schedule.update_adjusted_price'
    TASK_INDUSTRY_INDEX = 'schedule.update_industry_indexes'
    TASK_MARKET_ORDER = 'esi_region_order_price [%s]'
    
    # character related tasks
    TASK_CHARACTER_SKILLS = 'character_skill_update [%d]'
    
    def get_last_run_format(self):
        """ return the utc string date in iso format without ms and TZ info"""
        return self.last_run.replace(microsecond=0, tzinfo=None).isoformat(' ')
        
    def get_parsed_result(self):
        if not self.results_json:
            results_json = json.loads(self.results)
        return results_json