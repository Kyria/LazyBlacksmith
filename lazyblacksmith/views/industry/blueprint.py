# -*- encoding: utf-8 -*-
import config
from math import ceil

from flask import Blueprint
from flask import render_template
from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivitySkill
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import Item
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import ItemPrice
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
    
    # get science skill name, if applicable
    manufacturing_skills = item.activity_skills.filter_by(
        activity = Activity.ACTIVITY_MANUFACTURING,
    ).filter(
        ActivitySkill.skill_id != 3380 # industry
    )

    science_skill = []
    t2_manufacturing_skill = None
    for activity_skill in manufacturing_skills:
        if activity_skill.skill.market_group_id == 369:
            t2_manufacturing_skill = activity_skill.skill.name
        
        if activity_skill.skill.market_group_id == 375:
            science_skill.append(activity_skill.skill.name)
    
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
        't2_manufacturing_skill': t2_manufacturing_skill,
        'science_skill': science_skill,
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

    # calculate baseCost and build cost per ME
    base_cost = 0.0
    cost_per_me = {}
    materials = item.activity_materials.filter_by(activity=Activity.ACTIVITY_MANUFACTURING)
    for material in materials:
        item_adjusted_price = ItemAdjustedPrice.query.get(material.material_id)
        base_cost += item_adjusted_price.price * material.quantity
        
        # build cost
        price = ItemPrice.query.filter(
            ItemPrice.item_id == material.material_id,
            ItemPrice.region_id == 10000002,
        ).one()
        for level in xrange(0, 11):
            if level not in cost_per_me:
                cost_per_me[level] = {
                    'job_price_run': 0,
                    'job_price_max_run': 0,
                }
            me_bonus = (1.00 - level / 100.00)
            adjusted_quantity = max(1, me_bonus * material.quantity)
            job_price_run = max(1, ceil(adjusted_quantity)) * price.buy_price
            job_price_max_run = max(item.max_production_limit, ceil(item.max_production_limit * adjusted_quantity)) * price.buy_price
            
            cost_per_me[level]['job_price_run'] += job_price_run
            cost_per_me[level]['job_price_max_run'] += job_price_max_run

        
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
        'cost_per_me': cost_per_me,
    })

