from flask import Blueprint
from flask import render_template

from lazyblacksmith.cache import cache

template = Blueprint('template', __name__)

@template.route("/manufacturing/sublist/block")
@cache.cached(timeout=3600*24)
def manufacturing_sublist_block():
    return render_template('template/manufacturing-sublist-block.html')

@template.route("/manufacturing/sublist/row")
@cache.cached(timeout=3600*24)
def manufacturing_sublist_row():
    return render_template('template/manufacturing-sublist-row.html')

