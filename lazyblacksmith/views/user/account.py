# -*- encoding: utf-8 -*-
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required

from lazyblacksmith.models import Region
from lazyblacksmith.models import TaskStatus

account = Blueprint('account', __name__)


@account.route('/')
@login_required
def index():
    # get all tasks status
    skill_status = TaskStatus.query.get(
        TaskStatus.TASK_CHARACTER_SKILLS % current_user.character_id
    )
    
    # get region from pref price region (for display)
    all_regions = Region.query.filter(Region.wh == False).all()
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
    
    return render_template('account/account.html', **{
        'skill_status': skill_status,
        'invention_price_region': invention_price_region,
        'prod_price_region_minerals': prod_price_region_minerals,
        'prod_price_region_pi': prod_price_region_pi,
        'prod_price_region_moongoo': prod_price_region_moongoo,
        'prod_price_region_others': prod_price_region_others,
        'regions': all_regions,
    })
