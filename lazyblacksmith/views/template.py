# -*- encoding: utf-8 -*-
from flask import Blueprint
from flask import render_template

from lazyblacksmith.extension.cache import CACHE

template = Blueprint('template', __name__)


@template.route("/manufacturing/sublist/block")
@CACHE.cached(timeout=3600 * 24)
def manufacturing_sublist_block():
    return render_template('template/manufacturing-sublist-block.html')


@template.route("/manufacturing/sublist/row")
@CACHE.cached(timeout=3600 * 24)
def manufacturing_sublist_row():
    return render_template('template/manufacturing-sublist-row.html')


@template.route("/manufacturing/price/modal")
@CACHE.cached(timeout=3600 * 24)
def manufacturing_modal_price():
    return render_template('template/manufacturing-modal-price.html')
