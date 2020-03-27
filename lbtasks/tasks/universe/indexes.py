# -*- encoding: utf-8 -*-
""" Market indexes task """
from sqlalchemy.exc import SQLAlchemyError
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_industry_systems
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import db

from ... import celery_app, logger


@celery_app.task(name="universe.industry_indexes")
def task_industry_indexes():
    """ Get the industry indexes list from API. """
    all_indexes = esiclient.request(get_industry_systems())
    insert_index_list = []

    if all_indexes.status == 200:
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

        try:
            db.engine.execute("TRUNCATE TABLE %s" % IndustryIndex.__tablename__)
            db.engine.execute(
                IndustryIndex.__table__.insert(),
                insert_index_list
            )
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("Error while updating indexes")
