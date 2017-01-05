# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_industry_systems
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import TaskStatus
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from datetime import datetime
from email.utils import parsedate

import json
import pytz

@celery_app.task(name="schedule.update_industry_indexes")
def update_industry_index():
    """ Get the industry indexes list from API. """
    db.engine.execute("TRUNCATE TABLE %s" % IndustryIndex.__tablename__)
    db.session.commit()

    all_indexes = esiclient.request(get_industry_systems())

    insert_index_list = []

    for index in all_indexes.data:
        solar_system = index.solar_system_id

        for activity_index in index.cost_indices:
            row = {}
            row['solarsystem_id'] = solar_system
            row['activity'] = IndustryIndex.activity_string_to_activity(
                activity_index.activity
            )
            row['cost_index'] = activity_index.cost_index
            insert_index_list.append(row)

    db.engine.execute(
        IndustryIndex.__table__.insert(),
        insert_index_list
    )
    db.session.commit()

    task_status = TaskStatus(
        name='schedule.update_industry_indexes',
        expire=datetime(
            *parsedate(all_indexes.header['Expires'][0])[:6]
        ).replace(tzinfo=pytz.utc),
        last_run=utcnow(),
        results=json.dumps({'inserted': len(insert_index_list)})
    )
    db.session.merge(task_status)
    db.session.commit()
    
    return (len(insert_index_list), len(insert_index_list))
