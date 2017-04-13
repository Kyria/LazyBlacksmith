# -*- encoding: utf-8 -*-
import config

from flask import Blueprint as FlaskBlueprint
from flask import abort
from flask import render_template
from flask_login import current_user

from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivitySkill
from lazyblacksmith.models import Blueprint
from lazyblacksmith.models import Decryptor
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import Item
from lazyblacksmith.models import Region
from lazyblacksmith.models import SolarSystem
from lazyblacksmith.models import User
from lazyblacksmith.utils.industry import calculate_base_cost
from lazyblacksmith.utils.industry import calculate_build_cost
from lazyblacksmith.utils.industry import get_common_industry_skill
from lazyblacksmith.utils.industry import get_skill_data

blueprint = FlaskBlueprint('blueprint', __name__)


@blueprint.route('/')
def search():
    """ Display the blueprint search page """
    blueprints = Blueprint.query.join(User, Item).filter(
        (
            (Blueprint.character_id == current_user.character_id) |
            (
                (Blueprint.character_id == User.character_id) &
                (User.main_character_id == current_user.character_id)
            )
        ),
    ).order_by(
        Blueprint.corporation.asc(),
        Blueprint.original.asc(),
        Item.name.asc(),
    ).all()

    return render_template('blueprint/search.html', ** {
        'blueprints': blueprints,
    })


@blueprint.route('/manufacturing/<int:item_id>')
def manufacturing(item_id):
    """ Display the manufacturing page with all data """
    item = Item.query.get(item_id)
    char = current_user.pref.prod_character

    if item is None or item.max_production_limit is None:
        abort(404)

    activity = item.activities.filter_by(
        activity=Activity.ACTIVITY_MANUFACTURING
    ).one()
    materials = item.activity_materials.filter_by(
        activity=Activity.ACTIVITY_MANUFACTURING
    )
    product = item.activity_products.filter_by(
        activity=Activity.ACTIVITY_MANUFACTURING
    ).one()

    regions = Region.query.filter(
        Region.id.in_(config.ESI_REGION_PRICE)
    ).filter_by(
        wh=False
    )

    # get science skill name, if applicable
    manufacturing_skills = item.activity_skills.filter_by(
        activity=Activity.ACTIVITY_MANUFACTURING,
    ).filter(
        ActivitySkill.skill_id != 3380  # industry
    )

    science_skill = []
    t2_manufacturing_skill = None
    for activity_skill in manufacturing_skills:
        skill = get_skill_data(activity_skill.skill, char)
        if activity_skill.skill.market_group_id == 369:
            t2_manufacturing_skill = skill

        if activity_skill.skill.market_group_id == 375:
            science_skill.append(skill)

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
        'industry_skills': get_common_industry_skill(char),
    })


@blueprint.route('/research_copy/<int:item_id>')
def research(item_id):
    """ Display the research page with all price data pre calculated """
    item = Item.query.get(item_id)
    char = current_user.pref.research_character

    if item is None or item.max_production_limit is None:
        abort(404)

    activity_material = item.activities.filter_by(
        activity=Activity.ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY
    ).one()

    activity_time = item.activities.filter_by(
        activity=Activity.ACTIVITY_RESEARCHING_TIME_EFFICIENCY
    ).one()

    activity_copy = item.activities.filter_by(
        activity=Activity.ACTIVITY_COPYING
    ).one()

    # indexes
    indexes = IndustryIndex.query.filter(
        IndustryIndex.solarsystem_id == SolarSystem.id,
        SolarSystem.name == current_user.pref.research_system,
        IndustryIndex.activity.in_([
            Activity.ACTIVITY_COPYING,
            Activity.ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY,
            Activity.ACTIVITY_RESEARCHING_TIME_EFFICIENCY,
        ])
    )
    index_list = {}
    for index in indexes:
        index_list[index.activity] = index.cost_index

    # calculate baseCost and build cost per ME
    materials = item.activity_materials.filter_by(
        activity=Activity.ACTIVITY_MANUFACTURING
    )
    base_cost = calculate_base_cost(materials)
    cost = calculate_build_cost(
        materials,
        10000002,
        xrange(0, 11),
        item.max_production_limit
    )

    cost_prev_me = cost[0]['run']
    cost_prev_me_max = cost[0]['max_bpc_run']
    for level in xrange(0, 11):
        # cost
        current_cost = cost[level]['run']
        delta_me0 = cost[0]['run'] - current_cost
        delta_prev_me = cost_prev_me - current_cost
        delta_pct_me0 = (1 - current_cost / cost[0]['run']) * 100
        delta_pct_prev_me = (1 - current_cost / cost_prev_me) * 100

        current_cost = cost[level]['max_bpc_run']
        max_delta_me0 = cost[0]['max_bpc_run'] - current_cost
        max_delta_prev_me = cost_prev_me_max - current_cost
        max_delta_pct_me0 = (1 - current_cost / cost[0]['max_bpc_run']) * 100
        max_delta_pct_prev_me = (1 - current_cost / cost_prev_me_max) * 100

        cost[level].update({
            'delta_me0': delta_me0,
            'delta_prev_me': delta_prev_me,
            'delta_pct_me0': delta_pct_me0,
            'delta_pct_prev_me': delta_pct_prev_me,
            'max_delta_me0': max_delta_me0,
            'max_delta_prev_me': max_delta_prev_me,
            'max_delta_pct_me0': max_delta_pct_me0,
            'max_delta_pct_prev_me': max_delta_pct_prev_me,
        })

        cost_prev_me = cost[level]['run']
        cost_prev_me_max = cost[level]['max_bpc_run']

    me_time = {}
    te_time = {}
    for level in xrange(1, 11):
        # time
        level_modifier = (250 * 2**(1.25 * level - 2.5) / 105)
        me_duration = activity_material.time * level_modifier
        te_duration = activity_time.time * level_modifier
        me_cost = (
            base_cost * 0.02 * level_modifier * 1.1 *
            index_list[Activity.ACTIVITY_RESEARCHING_MATERIAL_EFFICIENCY]
        )
        te_cost = (
            base_cost * 0.02 * level_modifier * 1.1 *
            index_list[Activity.ACTIVITY_RESEARCHING_TIME_EFFICIENCY]
        )

        me_time[level] = {
            'duration': float("%0.2f" % me_duration),
            'cost': me_cost,
        }
        te_time[level] = {
            'duration': float("%0.2f" % te_duration),
            'cost': te_cost,
        }

    # display
    return render_template('blueprint/research.html', **{
        'blueprint': item,
        'activity_copy': activity_copy,
        'activity_material': activity_material,
        'activity_time': activity_time,
        'base_cost': base_cost,
        'index_list': index_list,
        'cost_per_me': cost,
        'industry_skills': get_common_industry_skill(char),
        'me_time': me_time,
        'te_time': te_time,
    })


@blueprint.route('/invention/<int:item_id>')
def invention(item_id):
    """ Display the invention page with all price data pre calculated """
    item = Item.query.get(item_id)
    char = current_user.pref.invention_character

    if item is None or item.max_production_limit is None:
        abort(404)

    # global activity
    activity_copy = item.activities.filter_by(
        activity=Activity.ACTIVITY_COPYING
    ).first()

    invention_skills = item.activity_skills.filter_by(
        activity=Activity.ACTIVITY_INVENTION
    ).all()

    # copy stuff
    copy_base_cost = 0.0
    if activity_copy is not None:
        # copy base cost, as it's different from the invention
        materials = item.activity_materials.filter_by(
            activity=Activity.ACTIVITY_MANUFACTURING
        )
        copy_base_cost = calculate_base_cost(materials)

    # loop through skills for display as we need to do the difference
    # between both skills (not the same bonuses in invention probability)
    encryption_skill = None
    datacore_skills = []
    for s in invention_skills:
        skill = get_skill_data(s.skill, char)
        if skill.name.find('Encryption') == -1:
            datacore_skills.append(skill)
        else:
            encryption_skill = skill

    # other skills

    # calculate baseCost for invention
    materials = item.activity_products.filter_by(
        activity=Activity.ACTIVITY_INVENTION
    ).first().product.activity_materials.filter_by(
        activity=Activity.ACTIVITY_MANUFACTURING
    )
    invention_base_cost = calculate_base_cost(materials)

    # base solar system
    indexes = IndustryIndex.query.filter(
        IndustryIndex.solarsystem_id == SolarSystem.id,
        SolarSystem.name == current_user.pref.invention_system,
        IndustryIndex.activity.in_([
            Activity.ACTIVITY_COPYING,
            Activity.ACTIVITY_INVENTION,
        ])
    )

    index_list = {}
    for index in indexes:
        index_list[index.activity] = index.cost_index

    # get decryptor
    decryptors = Decryptor.query.all()

    # get regions
    regions = Region.query.filter(
        Region.id.in_(config.ESI_REGION_PRICE)
    ).filter_by(
        wh=False
    )

    # display
    return render_template('blueprint/invention.html', **{
        'blueprint': item,
        'activity_copy': activity_copy,
        'activity_invention': item.activities.filter_by(
            activity=Activity.ACTIVITY_INVENTION
        ).one(),
        'copy_base_cost': copy_base_cost,
        'invention_base_cost': invention_base_cost,
        'datacore_skills': datacore_skills,
        'decryptors': decryptors,
        'encryption_skill': encryption_skill,
        'index_list': index_list,
        'invention_materials': item.activity_materials.filter_by(
            activity=Activity.ACTIVITY_INVENTION
        ).all(),
        'invention_products': item.activity_products.filter_by(
            activity=Activity.ACTIVITY_INVENTION
        ).all(),
        'regions': regions,
        'industry_skills': get_common_industry_skill(char),
    })
