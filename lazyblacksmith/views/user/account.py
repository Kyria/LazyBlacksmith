# -*- encoding: utf-8 -*-
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required
from sqlalchemy import or_

from lazyblacksmith.models import Region
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import User

account = Blueprint('account', __name__)


@account.route('/')
@login_required
def index():
    # get region from pref price region (for display)
    all_regions = Region.query.filter(Region.wh.is_(False)).all()
    the_forge_region = Region.query.get(10000002)

    invention_price_region = Region.query.get(
        current_user.pref.invention_price_region
    )
    prod_price_region_minerals = Region.query.get(
        current_user.pref.prod_price_region_minerals
    )
    prod_price_region_pi = Region.query.get(
        current_user.pref.prod_price_region_pi
    )
    prod_price_region_moongoo = Region.query.get(
        current_user.pref.prod_price_region_moongoo
    )
    prod_price_region_others = Region.query.get(
        current_user.pref.prod_price_region_others
    )
    reaction_price_region = Region.query.get(
        current_user.pref.reaction_price_regions
    )
    # if no region is found (wrong number) set the default to the forge
    if not invention_price_region:
        invention_price_region = the_forge_region
    if not prod_price_region_minerals:
        prod_price_region_minerals = the_forge_region
    if not prod_price_region_pi:
        prod_price_region_pi = the_forge_region
    if not prod_price_region_moongoo:
        prod_price_region_moongoo = the_forge_region
    if not prod_price_region_others:
        prod_price_region_others = the_forge_region
    if not reaction_price_region:
        reaction_price_region = the_forge_region

    # get all characters that have skill scope attached to them
    list_character_skills = User.query.filter(
        User.character_id == TokenScope.user_id,
        TokenScope.scope == TokenScope.SCOPE_SKILL,
        or_(
            User.character_id == current_user.character_id,
            User.main_character_id == current_user.character_id,
        )
    ).all()

    return render_template('account/account.html', **{
        'invention_price_region': invention_price_region,
        'prod_price_region_minerals': prod_price_region_minerals,
        'prod_price_region_pi': prod_price_region_pi,
        'prod_price_region_moongoo': prod_price_region_moongoo,
        'prod_price_region_others': prod_price_region_others,
        'reaction_price_region': reaction_price_region,
        'list_character_skills': list_character_skills,
        'regions': all_regions,
    })
