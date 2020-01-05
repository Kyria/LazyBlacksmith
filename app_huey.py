# -*- encoding: utf-8 -*-
# pylint: disable=unused-import
# flake8: noqa
""" entry point for huey_consumer """
import logging

from lbtasks import HUEY as app
from lbtasks.tasks import task_adjusted_price_base_cost
from lbtasks.tasks import task_industry_indexes
from lbtasks.tasks import task_market_orders

# disable / enable loggers we want
logging.getLogger('pyswagger').setLevel(logging.ERROR)
logging.getLogger('lb.tasks').setLevel(logging.WARNING)

