# -*- encoding: utf-8 -*-
import config

from flask import Blueprint
from flask import render_template

from lazyblacksmith.models import Item
from lazyblacksmith.models import OreRefining

ore = Blueprint('ore', __name__)


@ore.route("/")
def refining_index():
    refining = OreRefining.query.filter(
        OreRefining.is_compressed.is_(False)
    ).join(
        OreRefining.ore
    ).order_by(
        Item.market_group_id,
        'ore_id'
    )

    ore_list = {}
    ice_list = {}

    return ""
    # return render_template('price/price.html', **{
    #     'regions': regions,
    # })
