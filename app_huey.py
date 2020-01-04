# -*- encoding: utf-8 -*-
# pylint: disable=unused-import
# flake8: noqa
""" entry point for huey_consumer """
import logging

from lbtasks import HUEY as app
from lbtasks.tasks import task_update_industry_indexes
from lbtasks.tasks import task_update_adjusted_price_base_cost

# disable / enable loggers we want
logging.getLogger('pyswagger').setLevel(logging.ERROR)
logging.getLogger('lb.tasks').setLevel(logging.WARNING)

