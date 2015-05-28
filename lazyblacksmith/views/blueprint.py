from flask import Blueprint, render_template, abort

from lazyblacksmith.models import Item
from lazyblacksmith.models import Activity

blueprint = Blueprint('blueprint', __name__)

@blueprint.route('/manufacturing/<int:item_id>')
def manufacturing(item_id):
    """
    Display the manufacturing page with all data
    """
    item = Item.query.get(item_id)
    materials = item.activity_materials.filter_by(activity=Activity.ACTIVITY_MANUFACTURING)

    # is any of the materials manufactured ?
    has_manufactured_components = False

    for material in materials:
        if material.material.is_manufactured():
            has_manufactured_components = True
            break;

    return render_template('blueprint/manufacturing.html', **{
        'blueprint' : item,
        'materials': materials,
        'has_manufactured_components': has_manufactured_components,
    })


@blueprint.route('/')
def search():
    return render_template('blueprint/search.html')

