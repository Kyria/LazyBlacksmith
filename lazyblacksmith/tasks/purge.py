# -*- encoding: utf-8 -*-
import config
import datetime

from .lb_task import LbTask

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow


@celery_app.task(name="purge", base=LbTask, bind=True)
def task_purge(self):
    """ Purge all old stuff everywhere. """
    self.start()

    # purge all old TaskState objects
    purge_date_limit = utcnow() - datetime.timedelta(days=config.PURGE_OLD_TASKS)
    TaskState.query.filter(TaskState.end_date < purge_date_limit).delete()
    db.session.commit()

    # purge all tokens people never updated
    purge_date_limit = utcnow() - datetime.timedelta(days=config.PURGE_INVALID_TOKENS)
    TokenScope.query.filter_by(
        valid=False
    ).filter(
        ((TokenScope.last_update.is_(None)) & (TokenScope.updated_at <= purge_date_limit)) |
        (TokenScope.last_update < purge_date_limit)
    ).delete()
    db.session.commit()

    # purge old market data
    purge_date_limit = utcnow() - datetime.timedelta(days=config.PURGE_OLD_PRICES)
    ItemPrice.query.filter(ItemPrice.updated_at < purge_date_limit).delete()
    db.session.commit()

    self.end(TaskState.SUCCESS)
