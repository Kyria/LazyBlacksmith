# -*- encoding: utf-8 -*-
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import db
from lazyblacksmith.utils.crestutils import get_all_items
from lazyblacksmith.utils.crestutils import get_crest
from lazyblacksmith.utils.time import utcnow


def get_industry_index():
    """ Connect to the public CREST and get the industry indexes list. """
    crest = get_crest()
    industry_system_page = crest.industry.systems()

    insert_index_list = []

    # get all indexes
    all_indexes = get_all_items(industry_system_page)

    # TODO: get the date from headers
    # check if the data are not still from cache and if we don't already have them.
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
