# -*- encoding: utf-8 -*-
from collections import OrderedDict
from math import ceil

from flask import Blueprint
from flask import json
from flask import jsonify
from flask import request
from flask_login import current_user
from sqlalchemy.orm.exc import NoResultFound

from . import is_not_ajax
from lazyblacksmith.extension.cache import cache
from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivityMaterial
from lazyblacksmith.models import Item
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import SolarSystem


ajax_eve_sde = Blueprint('ajax_eve_sde', __name__)


@ajax_eve_sde.route('/blueprint/search/<string:name>', methods=['GET'])
def blueprint_search(name):
    """
    Return JSON result for a specific search
    name is the request name.
    """
    if request.is_xhr:
        cache_key = 'blueprint:search:%s' % (name.lower().replace(" ", ""),)

        data = cache.get(cache_key)
        if data is None:
            blueprints = Item.query.filter(
                Item.name.ilike('%' + name.lower() + '%'),
                Item.max_production_limit.isnot(None)
            ).order_by(
                Item.name.asc()
            ).all()

            data = []
            for bp in blueprints:
                invention_product = bp.activity_products.filter_by(
                    activity=Activity.ACTIVITY_INVENTION
                ).first()
                invention = False if invention_product is None else True

                data.append({
                    'id': bp.id,
                    'name': bp.name,
                    'invention': invention
                })

            # cache for 7 day as it does not change that often
            cache.set(cache_key, json.dumps(data), 24 * 3600 * 7)

        else:
            data = json.loads(data)

        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403


@ajax_eve_sde.route('/blueprint/bom/<int:blueprint_id>', methods=['GET'])
@cache.memoize(timeout=3600 * 24 * 7, unless=is_not_ajax)
def blueprint_bom(blueprint_id):
    """
    Return JSON with the list of all bill of material for
    each material in the blueprint given in argument
    """
    if request.is_xhr:
        blueprints = ActivityMaterial.query.filter_by(
            item_id=blueprint_id,
            activity=Activity.ACTIVITY_MANUFACTURING
        ).all()

        data = OrderedDict()
        for bp in blueprints:

            # As some item cannot be manufactured, catch the exception
            try:
                product = bp.material.product_for_activities
                product = product.filter_by(
                    activity=Activity.ACTIVITY_MANUFACTURING
                ).one()
                bp_final = product.blueprint
            except NoResultFound:
                continue

            activity = bp_final.activities.filter_by(
                activity=Activity.ACTIVITY_MANUFACTURING
            ).one()

            mats = bp_final.activity_materials.filter_by(
                activity=Activity.ACTIVITY_MANUFACTURING
            ).all()

            if bp_final.id not in data:
                data[bp_final.id] = {
                    'id': bp_final.id,
                    'icon': bp_final.icon_32(),
                    'name': bp_final.name,
                    'materials': [],
                    'time': activity.time,
                    'product_id': bp.material.id,
                    'product_name': bp.material.name,
                    'product_qty_per_run': product.quantity,
                }

            for mat in mats:
                pref = current_user.pref
                
                if mat.material.is_moon_goo():
                    price_type = pref.prod_price_type_moongoo
                    price_region = pref.prod_price_region_moongoo
                elif mat.material.is_pi():
                    price_type = pref.prod_price_type_pi
                    price_region = pref.prod_price_region_pi
                elif mat.material.is_mineral_salvage():
                    price_type = pref.prod_price_type_minerals
                    price_region = pref.prod_price_region_minerals
                else:
                    price_type = pref.prod_price_type_others
                    price_region = pref.prod_price_region_others
                    
                data[bp_final.id]['materials'].append({
                    'id': mat.material.id,
                    'name': mat.material.name,
                    'quantity': mat.quantity,
                    'icon': mat.material.icon_32(),
                    'price_type': price_type,
                    'price_region': price_region,
                })

        return jsonify(result=data.values())

    else:
        return 'Cannot call this page directly', 403


@ajax_eve_sde.route('/solarsystem/list', methods=['GET'])
@cache.cached(timeout=3600 * 24 * 7, unless=is_not_ajax)
def solarsystems():
    """
    Return JSON result with system list (ID,Name)
    """
    if request.is_xhr:
        systems = SolarSystem.query.all()
        data = []
        for system in systems:
            data.append(system.name)
        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403


@ajax_eve_sde.route('/item/search/<string:name>', methods=['GET'])
def item_search(name):
    """
    Return JSON result for a specific search
    name is the request name.
    """
    if request.is_xhr:
        cache_key = 'item:search:%s' % (name.lower().replace(" ", ""),)

        data = cache.get(cache_key)
        if data is None:
            items = Item.query.filter(
                Item.name.ilike('%' + name.lower() + '%'),
            ).order_by(
                Item.name.asc()
            ).all()

            data = []
            for item in items:
                data.append({
                    'id': item.id,
                    'name': item.name,
                    'icon': item.icon_32(),
                })

            # cache for 7 day as it does not change that often
            cache.set(cache_key, json.dumps(data), 24 * 3600 * 7)

        else:
            data = json.loads(data)

        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403


@ajax_eve_sde.route(
    '/item/buildcost/<int:blueprint_id>/<int:region_id>/<string:material_efficiency>',
    methods=['GET']
)
def build_cost_item(material_efficiency, blueprint_id, region_id):
    """
    Return JSON with the list of all costs for the given blueprint
    and all the material efficiency level
    """
    material_list = ActivityMaterial.query.filter_by(
        item_id=blueprint_id,
        activity=Activity.ACTIVITY_MANUFACTURING
    ).all()

    me_list = material_efficiency.split(',')
    build_cost = {}
    for mat in material_list:
        try:
            price = ItemPrice.query.filter(
                ItemPrice.region_id == region_id,
                ItemPrice.item_id == mat.material_id,
            ).one()
        except NoResultFound:
            continue

        for ume in me_list:
            me = int(ume)
            if me not in build_cost:
                build_cost[me] = 0
            quantity = max(1, ceil(mat.quantity * (1.00 - me / 100.00)))
            price_value = price.sell_price if price.sell_price is not None else price.buy_price
            build_cost[me] += quantity * price_value

    return jsonify({'prices': build_cost, 'region': region_id})
