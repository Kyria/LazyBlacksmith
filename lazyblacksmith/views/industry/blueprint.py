# -*- encoding: utf-8 -*-
import config

from flask import Blueprint
from flask import render_template
from lazyblacksmith.models import Activity
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import Item
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import SolarSystem

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
    regions = Region.query.filter(
        Region.id.in_(config.CREST_REGION_PRICE)
    ).filter_by(
        wh=False
    )

    # is any of the materials manufactured ?
    has_manufactured_components = False

    for material in materials:
        if material.material.is_manufactured():
            has_manufactured_components = True
            break

    return render_template('blueprint/manufacturing.html', **{
        'blueprint': item,
        'materials': materials,
        'activity': activity,
        'product': product,
        'regions': regions,
        'has_manufactured_components': has_manufactured_components,
    })


@blueprint.route('/')
def search():
    return render_template('blueprint/search.html')


@blueprint.route('/research_copy/<int:item_id>')
def research_and_copy(item_id):
    item = Item.query.get(item_id)

    activity_material = item.activities.filter_by(
        activity=Activity.ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY
    ).one()

    activity_time = item.activities.filter_by(
        activity=Activity.ACTIVITY_RESEARCHING_TIME_EFFICIENCY
    ).one()

    activity_copy = item.activities.filter_by(
        activity=Activity.ACTIVITY_COPYING
    ).one()

    # calculate baseCost
    base_cost = 0.0
    materials = item.activity_materials.filter_by(activity=Activity.ACTIVITY_MANUFACTURING)
    for material in materials:
        item_adjusted_price = ItemAdjustedPrice.query.get(material.material_id)
        base_cost += item_adjusted_price.price * material.quantity

    # base solar system : 30000142 = Jita
    indexes = IndustryIndex.query.filter(
        IndustryIndex.solarsystem_id == 30000142,
        IndustryIndex.activity.in_([
            Activity.ACTIVITY_COPYING,
            Activity.ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY,
            Activity.ACTIVITY_RESEARCHING_TIME_EFFICIENCY,
        ])
    )
    
    index_list = {}
    for index in indexes:
        index_list[index.activity] = index.cost_index

    # display
    return render_template('blueprint/research.html', **{
        'blueprint': item,
        'activity_material': activity_material,
        'activity_time': activity_time,
        'activity_copy': activity_copy,
        'base_cost': base_cost,
        'index_list': index_list,
    })


# researchTime = baseResearchTime * timeModifier * levelModifier / 105
# researchFee = baseJobCost * systemCostIndex * 0.02 * levelModifier / 105
# copyTime = baseCopyTime * runs * runsPerCopy * timeModifier
# copyFee = baseJobCost * systemCostIndex * 0.02 * runs * runsPerCopy
