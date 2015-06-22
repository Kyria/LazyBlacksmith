# -*- encoding: utf-8 -*-
import pycrest
import datetime

import lazyblacksmith.utils.crestutils
from lazyblacksmith.models import db
from lazyblacksmith.models import IndustryIndex

def get_industry_index():
    """
    Connect to the public CREST and get the industry indexes list.
    """
    crest = crestutils.get_crest()
    industry_system_page = crest.industry.systems()

    insert_index_list = []

    # get all indexes
    all_indexes = crestutils.get_all_items(industry_system_page)

    # TODO: get the date from headers
    # check if the data are not still from cache and if we don't already have them.  
    date = datetime.utcnow()

    for index in all_indexes:
        solar_system = industry_system_page.solarSystem.id

        for activity_index in index.systemCostIndices:
            row = {}
            row['solarsystem_id'] = solar_system
            row['date'] = date
            row['activity'] = index.solarSystem.id
            row['cost_index'] = index.solarSystem.id
            insert_index_list.append(row)

    db.engine.execute(
        IndustryIndex.__table__.insert(),
        insert_index_list
    )
