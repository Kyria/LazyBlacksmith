# -*- encoding: utf-8 -*-
from flask import abort
from flask import Blueprint
from flask import render_template

from lazyblacksmith.models import Item
from lazyblacksmith.models import Activity
from lazyblacksmith.models import Region

blueprint = Blueprint('blueprint', __name__)

@blueprint.route('/manufacturing/<int:item_id>')
def manufacturing(item_id):
    """
    Display the manufacturing page with all data
    """
    item = Item.query.get(item_id)
    activity = item.activities.filter_by(activity=Activity.ACTIVITY_MANUFACTURING).one()
    materials = item.activity_materials.filter_by(activity=Activity.ACTIVITY_MANUFACTURING)
    product = item.activity_products.filter_by(activity=Activity.ACTIVITY_MANUFACTURING).one()
    regions = Region.query.filter_by(wh=False)

    # is any of the materials manufactured ?
    has_manufactured_components = False

    for material in materials:
        if material.material.is_manufactured():
            has_manufactured_components = True
            break;

    return render_template('blueprint/manufacturing.html', **{
        'blueprint' : item,
        'materials': materials,
        'activity' : activity,
        'product' : product,
        'regions' : regions,
        'has_manufactured_components': has_manufactured_components,
    })


@blueprint.route('/')
def search():
    return render_template('blueprint/search.html')

