# -*- encoding: utf-8 -*-
""" Module for all task things in lazyblacksmith """
import logging
from .flask_celery import celery_app # noqa

logger = logging.getLogger('lb.tasks')  # noqa
