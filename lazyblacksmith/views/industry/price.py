# -*- encoding: utf-8 -*-
import config

from flask import Blueprint
from flask import render_template

from lazyblacksmith.models import Region

price = Blueprint('price', __name__)


@price.route("/")
def index():
    regions = Region.query.filter(
        Region.id.in_(config.ESI_REGION_PRICE)
    ).filter_by(
        wh=False
    ).order_by(
        Region.name
    )

    return render_template('price/price.html', **{
        'regions': regions,
    })
