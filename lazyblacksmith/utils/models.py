# -*- encoding: utf-8 -*-
""" Utils with shortcuts for common models query """
from lazyblacksmith.models import Region

import config


def get_regions(is_wh=False):
    """ return the list of regions """
    return Region.query.filter(
        Region.id.in_(config.ESI_REGION_PRICE)
    ).filter_by(
        wh=is_wh
    )
