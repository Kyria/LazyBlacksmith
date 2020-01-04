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
from lazyblacksmith.models import ActivityProduct
from lazyblacksmith.models import Item
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import SolarSystem
from lazyblacksmith.models import db
from lazyblacksmith.models.enums import ActivityEnum


ajax_eve_sde = Blueprint('ajax_eve_sde', __name__)


@ajax_eve_sde.route('/blueprint/search/<string:name>', methods=['GET'])
@CACHE.memoize(timeout=3600 * 24 * 7, unless=is_not_ajax)
def blueprint_search(name):
    """
    Return JSON result for a specific search
    name is the request name.
    """
    if request.is_xhr:
        name_lower = name.lower()

        # prevent only % string, to avoid query the full database at once...
        if name_lower == '%' * len(name_lower):
            return jsonify(result=[])

        blueprints = Item.query.filter(
            Item.name.ilike('%' + name_lower + '%'),
            Item.max_production_limit.isnot(None)
        ).outerjoin(
            ActivityProduct,
            (
                (Item.id == ActivityProduct.item_id) & (
                    (ActivityProduct.activity == ActivityEnum.INVENTION.aid) |
                    (ActivityProduct.activity == ActivityEnum.REACTIONS.aid)
                )
            )
        ).options(
            db.contains_eager(Item.activity_products__eager)
        ).order_by(
            Item.name.asc()
        ).all()

        data = []
        for bp in blueprints:
            invention = False
            reaction = False

            # we can't have invention AND reaction
            # at the same time as product.
            if bp.activity_products__eager:
                invention = (
                    bp.activity_products__eager[0].activity ==
                    ActivityEnum.INVENTION.aid
                )
                reaction = (
                    bp.activity_products__eager[0].activity ==
                    ActivityEnum.REACTIONS.aid
                )

            data.append({
                'id': bp.id,
                'name': bp.name,
                'invention': invention,
                'reaction': reaction,
                'relic': bp.is_ancient_relic(),
            })

        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403


@ajax_eve_sde.route('/blueprint/bom/<int:blueprint_id>', methods=['GET'])
def blueprint_bom(blueprint_id):
    """
    Return JSON with the list of all bill of material for
    each material in the blueprint given in argument

    As reaction and manufacturing cannot happen on the same blueprint at once
    we can safely ask for both at the same time (to be used in prod/reactions)
    """
    if request.is_xhr:
        blueprints = ActivityMaterial.query.filter(
            ActivityMaterial.item_id == blueprint_id,
            (
                (ActivityMaterial.activity == ActivityEnum.MANUFACTURING.aid) |
                (ActivityMaterial.activity == ActivityEnum.REACTIONS.aid)
            )
        ).all()

        data = OrderedDict()
        for bp in blueprints:
            # As some item cannot be manufactured, catch the exception
            try:
                product = bp.material.product_for_activities
                product = product.filter(
                    (ActivityProduct.activity == ActivityEnum.MANUFACTURING.aid) |
                    (ActivityProduct.activity == ActivityEnum.REACTIONS.aid)
                ).one()
                bp_final = product.blueprint
            except NoResultFound:
                continue

            activity = bp_final.activities.filter(
                (Activity.activity == ActivityEnum.MANUFACTURING.aid) |
                (Activity.activity == ActivityEnum.REACTIONS.aid)
            ).one()

            mats = bp_final.activity_materials.filter(
                (ActivityMaterial.activity == ActivityEnum.MANUFACTURING.aid) |
                (ActivityMaterial.activity == ActivityEnum.REACTIONS.aid)
            ).all()

            if bp_final.id not in data:
                data[bp_final.id] = {
                    'id': bp_final.id,
                    'icon': bp_final.icon_32(),
                    'name': bp_final.name,
                    'volume': bp.material.volume,
                    'materials': [],
                    'time': activity.time,
                    'product_id': bp.material.id,
                    'product_name': bp.material.name,
                    'product_qty_per_run': product.quantity,
                    'max_run_per_bp': bp_final.max_production_limit,
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
                    'volume': mat.material.volume,
                    'icon': mat.material.icon_32(),
                    'price_type': price_type,
                    'price_region': price_region,
                })

        return jsonify(result=list(data.values()))

    else:
        return 'Cannot call this page directly', 403


@ajax_eve_sde.route('/solarsystem/list', methods=['GET'])
@CACHE.cached(timeout=3600 * 24 * 7, unless=is_not_ajax)
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
@CACHE.memoize(timeout=3600 * 24 * 7, unless=is_not_ajax)
def item_search(name):
    """
    Return JSON result for a specific search
    name is the request name.
    """
    if request.is_xhr:
        cache_key = 'item:search:%s' % (name.lower().replace(" ", ""),)

        data = CACHE.get(cache_key)
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
            CACHE.set(cache_key, json.dumps(data), 24 * 3600 * 7)

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
        activity=ActivityEnum.MANUFACTURING.aid
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
