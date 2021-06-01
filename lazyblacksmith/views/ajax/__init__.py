# -*- encoding: utf-8 -*-
from flask import request
from lazyblacksmith.utils.request import is_xhr

import logging

logger = logging.getLogger('lb.ajax')


def is_not_ajax():
    """
    Return True if request is not ajax
    This function is used in @cache annotation
    to not cache direct call (http 403)
    """
    return not is_xhr(request)
