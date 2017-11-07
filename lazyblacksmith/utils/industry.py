# -*- encoding: utf-8 -*-
from collections import namedtuple
from math import ceil

from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import ItemPrice

from . import logger


def get_skill_data(skill, char):
    """ return formatted skill data to be used in the template """
    SkillData = namedtuple('SkillData', ['name', 'level'])
    if char:
        s = char.skills.filter_by(skill=skill).one_or_none()
        if s:
            return SkillData(skill.name, s.level)
    return SkillData(skill.name, 0)


def get_common_industry_skill(char):
    """ Return the "common" industry skills for a given char

    Return the level of the differents industry skills that are not blueprint
    specific for a given character (default level=0) :
    - science
    - metallurgy
    - research
    - industry
    - advanced industry
    """
    SKILL_SCIENCE_ID = 3402
    SKILL_ADV_INDUSTRY_ID = 3388
    SKILL_INDUSTRY = 3380
    SKILL_RESEARCH = 3403
    SKILL_METALLURGY = 3409
    SKILL_REACTIONS = 45746
    skills = {
        'science': 0,
        'industry': 0,
        'adv_industry': 0,
        'metallurgy': 0,
        'research': 0,
        'reactions': 0,
    }
    if char:
        science = char.skills.filter_by(
            skill_id=SKILL_SCIENCE_ID
        ).one_or_none()
        adv_industry = char.skills.filter_by(
            skill_id=SKILL_ADV_INDUSTRY_ID
        ).one_or_none()
        industry = char.skills.filter_by(
            skill_id=SKILL_INDUSTRY
        ).one_or_none()
        research = char.skills.filter_by(
            skill_id=SKILL_RESEARCH
        ).one_or_none()
        metallurgy = char.skills.filter_by(
            skill_id=SKILL_METALLURGY
        ).one_or_none()
        reactions = char.skills.filter_by(
            skill_id=SKILL_REACTIONS
        ).one_or_none()

        if science:
            skills['science'] = science.level
        if adv_industry:
            skills['adv_industry'] = adv_industry.level
        if industry:
            skills['industry'] = industry.level
        if research:
            skills['research'] = research.level
        if metallurgy:
            skills['metallurgy'] = metallurgy.level
        if reactions:
            skills['reactions'] = reactions.level

    return skills


def calculate_base_cost(material_list):
    """ Calculate the base cost using a list of activity_material """
    copy_base_cost = 0.0
    for material in material_list:
        item_adjusted_price = ItemAdjustedPrice.query.get(
            material.material_id
        )
        if item_adjusted_price:
            copy_base_cost += item_adjusted_price.price * material.quantity

    return copy_base_cost


def calculate_build_cost(material_list, region_id, me_list, max_run):
    """ Return the estimated build price for a given material_list

    Return the build price for a given material list, for research and
    invention, in a station without any bonuses
    """
    cost = {}
    for material in material_list:
        # build cost
        item_price = ItemPrice.query.filter(
            ItemPrice.item_id == material.material_id,
            ItemPrice.region_id == region_id,
        ).one_or_none()

        price = 0.0
        if not item_price:
            # if we don't have any price, use the adjusted
            # TODO: get the average price from ESI market for this.
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

        for level in me_list:
            if level not in cost:
                cost[level] = {
                    'run': 0,
                    'max_bpc_run': 0,
                }

            me_bonus = (1.00 - level / 100.00)
            adjusted_quantity = max(1, me_bonus * material.quantity)
            cost[level]['run'] += max(1, ceil(adjusted_quantity)) * price
            cost[level]['max_bpc_run'] += max(
                max_run,
                ceil(max_run * round(adjusted_quantity, 2))
            ) * price
    return cost
