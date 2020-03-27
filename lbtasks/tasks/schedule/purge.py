# -*- encoding: utf-8 -*-
""" Purging task """
import datetime
from sqlalchemy.exc import SQLAlchemyError

import config
from lazyblacksmith.models import ItemPrice, TokenScope, db
from lazyblacksmith.utils.time import utcnow

from ... import celery_app, logger


@celery_app.task(name="schedule.purge")
def task_purge():
    """ Purge all old stuff everywhere. """
    # purge all tokens people never updated

    try:
        purge_date_limit = (
            utcnow() - datetime.timedelta(days=config.PURGE_INVALID_TOKENS)
        )
        TokenScope.query.filter_by(
            valid=False
        ).filter(
            (
                (TokenScope.last_update.is_(None)) &
                (TokenScope.updated_at <= purge_date_limit)
            ) | (
                TokenScope.last_update < purge_date_limit
            )
        ).delete()
        db.session.commit()

        # purge old market data
        purge_date_limit = (
            utcnow() - datetime.timedelta(days=config.PURGE_OLD_PRICES)
        )
        ItemPrice.query.filter(ItemPrice.updated_at < purge_date_limit).delete()
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("Error while trying to purge data")
