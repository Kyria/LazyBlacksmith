# -*- encoding: utf-8 -*-
from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_crest
from lazyblacksmith.utils.time import utcnow


@celery_app.task(name="schedule.update_industry_indexes")
def update_industry_index():
    """ Connect to the public CREST and get the industry indexes list. """
    crest = get_crest()
    all_indexes = get_all_items(crest.industry.systems())

    insert_index_list = []

    date = utcnow()
    for index in all_indexes:
        solar_system = index.solarSystem.id

        for activity_index in index.systemCostIndices:
            row = {}
            row['solarsystem_id'] = solar_system
            row['date'] = date
            row['activity'] = activity_index.activityID
            row['cost_index'] = activity_index.costIndex
            insert_index_list.append(row)

    db.engine.execute(
        IndustryIndex.__table__.insert(),
        insert_index_list
    )
