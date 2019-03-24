# -*- encoding: utf-8 -*-
import config

from flask import Blueprint as FlaskBlueprint
from flask import abort
from flask import render_template
from flask import redirect
from flask_login import current_user

from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivityProduct
from lazyblacksmith.models import ActivitySkill
from lazyblacksmith.models import Blueprint
from lazyblacksmith.models import Decryptor
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import Item
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import Region
from lazyblacksmith.models import SolarSystem
from lazyblacksmith.models import User
from lazyblacksmith.models import db
from lazyblacksmith.models.enums import ActivityEnum
from lazyblacksmith.utils.industry import IGNORED_PROD_SKILLS
from lazyblacksmith.utils.industry import calculate_base_cost
from lazyblacksmith.utils.industry import calculate_build_cost
from lazyblacksmith.utils.industry import get_common_industry_skill
from lazyblacksmith.utils.industry import get_skill_data
from lazyblacksmith.utils.models import get_regions

blueprint = FlaskBlueprint('blueprint', __name__)


@blueprint.route('/')
def search():
    """ Display the blueprint search page """
    blueprints = []
    has_corp_bp = False

    if current_user.is_authenticated:
        blueprints = Blueprint.query.join(User, Item).filter(
            (
                (Blueprint.character_id == current_user.character_id) |
                (
                    (Blueprint.character_id == User.character_id) &
                    (User.main_character_id == current_user.character_id)
                )
            ),
        ).outerjoin(
            ActivityProduct,
            (Blueprint.item_id == ActivityProduct.item_id) & (
                (ActivityProduct.activity == ActivityEnum.INVENTION.id) |
                (ActivityProduct.activity == ActivityEnum.REACTIONS.id)
            )
        ).options(
            db.contains_eager(Blueprint.item)
            .contains_eager(Item.activity_products__eager)
        ).order_by(
            Blueprint.corporation.asc(),
            Blueprint.original.asc(),
            Item.name.asc(),
        ).all()

        # take the latest blueprint (as corp bp are at the end)
        # and check if it's a corp bp.
        if blueprints:
            has_corp_bp = blueprints[-1].corporation

    return render_template('blueprint/search.html', ** {
        'blueprints': blueprints,
        'has_corp_bp': has_corp_bp,
    })


@blueprint.route('/manufacturing/<int:item_id>')
@blueprint.route(('/manufacturing/<int:item_id>/'
                  '<int(min=0, max=10):me>/<int(min=0, max=20):te>'))
def manufacturing(item_id, me=0, te=0):
    """ Display the manufacturing page with all data """
    item = Item.query.get(item_id)
    char = current_user.pref.prod_character

    if item is None:
        abort(404)

    if item.max_production_limit is None:
        if item.is_from_manufacturing:
            activity_product = item.product_for_activities.filter_by(
                activity=ActivityEnum.MANUFACTURING.id
            ).one()
            return redirect(url_for(
                ".manufacturing",
                item_id=activity_product.item_id,
                me=me,
                te=te
            ))
        abort(404)

    activity = item.activities.filter_by(
        activity=ActivityEnum.MANUFACTURING.id
    ).one()
    materials = item.activity_materials.filter_by(
        activity=ActivityEnum.MANUFACTURING.id
    )
    product = item.activity_products.filter_by(
        activity=ActivityEnum.MANUFACTURING.id
    ).one()

    # get science skill name, if applicable
    manufacturing_skills = item.activity_skills.filter_by(
        activity=ActivityEnum.MANUFACTURING.id,
    ).filter(
        ActivitySkill.skill_id != 3380  # industry
    )

    science_skill = []
    t2_manufacturing_skill = None
    for activity_skill in manufacturing_skills:
        if activity_skill.skill_id in IGNORED_PROD_SKILLS:
            continue
        skill = get_skill_data(activity_skill.skill, char)
        if activity_skill.skill.market_group_id == 369:
            t2_manufacturing_skill = skill

        if activity_skill.skill.market_group_id == 375:
            science_skill.append(skill)

    # is any of the materials manufactured ?
    has_manufactured_components = False
    has_cap_part_components = False

    for material in materials:
        if material.material.is_from_manufacturing:
            has_manufactured_components = True
        if material.material.is_cap_part():
            has_cap_part_components = True

    return render_template('blueprint/manufacturing.html', **{
        'blueprint': item,
        'materials': materials,
        'activity': activity,
        'product': product,
        'regions': get_regions(),
        'has_manufactured_components': has_manufactured_components,
        'has_cap_part_components': has_cap_part_components,
        't2_manufacturing_skill': t2_manufacturing_skill,
        'science_skill': science_skill,
        'industry_skills': get_common_industry_skill(char),
        'me': me,
        'te': te,
    })


@blueprint.route('/research_copy/<int:item_id>')
def research(item_id):
    """ Display the research page with all price data pre calculated """
    item = Item.query.get(item_id)
    char = current_user.pref.research_character

    if item is None or item.max_production_limit is None:
        abort(404)

    activity_material = item.activities.filter_by(
        activity=ActivityEnum.RESEARCH_MATERIAL_EFFICIENCY.id
    ).one()

    activity_time = item.activities.filter_by(
        activity=ActivityEnum.RESEARCH_TIME_EFFICIENCY.id
    ).one()

    activity_copy = item.activities.filter_by(
        activity=ActivityEnum.COPYING.id
    ).one()

    research_activity_materials = item.activity_materials.all()

    # indexes
    indexes = IndustryIndex.query.filter(
        IndustryIndex.solarsystem_id == SolarSystem.id,
        SolarSystem.name == current_user.pref.research_system,
        IndustryIndex.activity.in_([
            ActivityEnum.COPYING.id,
            ActivityEnum.RESEARCH_MATERIAL_EFFICIENCY.id,
            ActivityEnum.RESEARCH_TIME_EFFICIENCY.id,
        ])
    )
    index_list = {}
    for index in indexes:
        index_list[index.activity] = index.cost_index

    # get materials and prices
    manufacturing_materials = item.activity_materials.filter_by(
        activity=ActivityEnum.MANUFACTURING.id
    ).all()

    prices = {}
    for material in manufacturing_materials:
        price = 0.0
        item_price = ItemPrice.query.filter(
            ItemPrice.item_id == material.material_id,
            ItemPrice.region_id == 10000002,
        ).one_or_none()
        if not item_price:
            item_adjusted_price = ItemAdjustedPrice.query.get(
                material.material_id
            )
            price = item_adjusted_price.price

        else:
            # we want the average price,
            # since this is used only in research/invention
            nb = 0.0
            if item_price.buy_price:
                price += item_price.buy_price
                nb += 1.0

            if item_price.sell_price:
                price += item_price.sell_price
                nb += 1.0

            price /= nb
        prices[material.material_id] = price

    me_time = {}
    te_time = {}
    for level in range(1, 11):
        # time
        level_modifier = (250 * 2**(1.25 * level - 2.5) / 105)
        me_duration = activity_material.time * level_modifier
        te_duration = activity_time.time * level_modifier
        me_cost = (
            item.base_cost * 0.02 * level_modifier * 1.1 *
            index_list[ActivityEnum.RESEARCH_MATERIAL_EFFICIENCY.id]
        )
        te_cost = (
            item.base_cost * 0.02 * level_modifier * 1.1 *
            index_list[ActivityEnum.RESEARCH_TIME_EFFICIENCY.id]
        )

        me_time[level] = {
            'duration': float("%0.2f" % me_duration),
            'cost': me_cost,
        }
        te_time[level] = {
            'duration': float("%0.2f" % te_duration),
            'cost': te_cost,
        }

    # get materials for all activities except manuf/reaction
    research_materials = {
        ActivityEnum.COPYING.id: {'total': 0, 'mats': []},
        ActivityEnum.RESEARCH_TIME_EFFICIENCY.id: {'total': 0, 'mats': []},
        ActivityEnum.RESEARCH_MATERIAL_EFFICIENCY.id: {'total': 0, 'mats': []},
    }

    for material in research_activity_materials:
        if material.activity in research_materials:
            mat_item = Item.query.get(material.material_id)

            mat_price = ItemPrice.query.filter_by(
                item_id=mat_item.id, region_id=10000002
            ).one_or_none()
            if mat_price is None:
                mat_price = 0
            else:
                mat_price = mat_price.sell_price

            research_materials[material.activity]['mats'].append({
                'id': material.material_id,
                'quantity': material.quantity,
                'item': mat_item,
                'price': mat_price
            })
            research_materials[material.activity]['total'] += (
                material.quantity * mat_price)

    # display
    return render_template('blueprint/research.html', **{
        'blueprint': item,
        'activity_copy': activity_copy,
        'activity_material': activity_material,
        'activity_time': activity_time,
        'base_cost': item.base_cost,
        'index_list': index_list,
        'industry_skills': get_common_industry_skill(char),
        'me_time': me_time,
        'te_time': te_time,
        'research_materials': research_materials,
        'manufacturing_materials': manufacturing_materials,
        'prices': prices,
    })


@blueprint.route('/invention/<int:item_id>')
def invention(item_id):
    """ Display the invention page with all price data pre calculated """
    item = Item.query.get(item_id)
    char = current_user.pref.invention_character

    if item is None or item.max_production_limit is None:
        activity_product = item.product_for_activities.filter_by(
            activity=ActivityEnum.INVENTION.id
        ).one_or_none()
        if activity_product is not None:
            return redirect(url_for(
                ".invention",
                item_id=activity_product.item_id
            ))
        abort(404)

    # global activity
    activity_copy = item.activities.filter_by(
        activity=ActivityEnum.COPYING.id
    ).first()

    invention_skills = item.activity_skills.filter_by(
        activity=ActivityEnum.INVENTION.id
    ).all()

    # copy stuff
    copy_base_cost = 0.0
    if activity_copy is not None:
        # copy base cost, as it's different from the invention
        materials = item.activity_materials.filter_by(
            activity=ActivityEnum.MANUFACTURING.id
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
        activity=ActivityEnum.INVENTION.id
    ).first().product.activity_materials.filter_by(
        activity=ActivityEnum.MANUFACTURING.id
    )
    invention_base_cost = calculate_base_cost(materials)

    # base solar system
    indexes = IndustryIndex.query.filter(
        IndustryIndex.solarsystem_id == SolarSystem.id,
        SolarSystem.name == current_user.pref.invention_system,
        IndustryIndex.activity.in_([
            ActivityEnum.COPYING.id,
            ActivityEnum.INVENTION.id,
        ])
    )

    index_list = {}
    for index in indexes:
        index_list[index.activity] = index.cost_index

    # get decryptor
    decryptors = Decryptor.query.all()

    # display
    return render_template('blueprint/invention.html', **{
        'blueprint': item,
        'activity_copy': activity_copy,
        'activity_invention': item.activities.filter_by(
            activity=ActivityEnum.INVENTION.id
        ).one(),
        'copy_base_cost': copy_base_cost,
        'invention_base_cost': invention_base_cost,
        'datacore_skills': datacore_skills,
        'decryptors': decryptors,
        'encryption_skill': encryption_skill,
        'index_list': index_list,
        'invention_materials': item.activity_materials.filter_by(
            activity=ActivityEnum.INVENTION.id
        ).all(),
        'invention_products': item.activity_products.filter_by(
            activity=ActivityEnum.INVENTION.id
        ).all(),
        'regions': get_regions(),
        'industry_skills': get_common_industry_skill(char),
    })


@blueprint.route('/reaction/<int:item_id>')
def reaction(item_id):
    """ Display the manufacturing page with all data """
    item = Item.query.get(item_id)
    char = current_user.pref.prod_character

    if item is None or item.max_production_limit is None:
        activity_product = item.product_for_activities.filter_by(
            activity=ActivityEnum.REACTIONS.id
        ).one_or_none()
        if activity_product is not None:
            return redirect(url_for(
                ".reaction",
                item_id=activity_product.item_id
            ))
        abort(404)

    activity = item.activities.filter_by(
        activity=ActivityEnum.REACTIONS.id
    ).one()
    materials = item.activity_materials.filter_by(
        activity=ActivityEnum.REACTIONS.id
    )
    product = item.activity_products.filter_by(
        activity=ActivityEnum.REACTIONS.id
    ).one()

    return render_template('blueprint/reaction.html', **{
        'blueprint': item,
        'materials': materials,
        'activity': activity,
        'product': product,
        'regions': get_regions(),
        'industry_skills': get_common_industry_skill(char),
    })
