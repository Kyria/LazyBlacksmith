# -*- encoding: utf-8 -*-
from collections import OrderedDict

from flask import Blueprint
from flask import json
from flask import jsonify
from flask import request
from sqlalchemy.orm.exc import NoResultFound

from lazyblacksmith.extension.cache import cache
from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivityMaterial
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import Item
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import ItemPrice
from lazyblacksmith.models import SolarSystem
from lazyblacksmith.utils.time import utcnow

import humanize

ajax = Blueprint('ajax', __name__)


def is_not_ajax():
    """
    Return True if request is not ajax
    This function is used in @cache annotation
    to not cache direct call (http 403)
    """
    return not request.is_xhr


@ajax.route('/blueprint/search/<string:name>', methods=['GET'])
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
                Item.name.ilike('%'+name.lower()+'%'),
                Item.max_production_limit.isnot(None)
            ).order_by(
                Item.name.asc()
            ).all()

            data = []
            for bp in blueprints:
                invention = False

                data.append({
                    'id': bp.id,
                    'name': bp.name,
                    'invention': invention
                })

            # cache for 7 day as it does not change that often
            cache.set(cache_key, json.dumps(data), 24*3600*7)

        else:
            data = json.loads(data)

        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403


@ajax.route('/blueprint/bom/<int:blueprint_id>', methods=['GET'])
@cache.memoize(timeout=3600*24*7, unless=is_not_ajax)
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
                data[bp_final.id]['materials'].append({
                    'id': mat.material.id,
                    'name': mat.material.name,
                    'quantity': mat.quantity,
                    'icon': mat.material.icon_32(),
                })

        return jsonify(result=data.values())

    else:
        return 'Cannot call this page directly', 403


@ajax.route('/solarsystem/list', methods=['GET'])
@cache.cached(timeout=3600*24*7, unless=is_not_ajax)
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


@ajax.route('/crest/get_price/<string:item_list>', methods=['GET'])
def get_price(item_list):
    """
    Get prices for all items we need !
    """
    if request.is_xhr:

        item_list = item_list.split(',')

        # get all items price
        item_prices = ItemPrice.query.filter(
            ItemPrice.item_id.in_(item_list)
        )

        item_price_list = {}
        for price in item_prices:
            if price.region_id not in item_price_list:
                item_price_list[price.region_id] = {}

            update_delta = price.updated_at - utcnow()
            item_price_list[price.region_id][price.item_id] = {
                'sell': price.sell_price,
                'buy': price.buy_price,
                'updated_at': humanize.naturaltime(update_delta),
            }

        # get all items adjusted price
        item_adjusted = ItemAdjustedPrice.query.filter(
            ItemAdjustedPrice.item_id.in_(item_list)
        )

        item_adjusted_list = {}
        for item in item_adjusted:
            item_adjusted_list[item.item_id] = item.price

        return jsonify({'prices': item_price_list, 'adjusted': item_adjusted_list})
    else:
        return 'Cannot call this page directly', 403


@ajax.route('/crest/get_index/<int:activity>/<string:solar_system_names>', methods=['GET'])
def get_index_activity(solar_system_names, activity):
    if Activity.check_activity_existence(activity):
        ss_name_list = solar_system_names.split(',')

        # get the solar systems
        solar_systems = SolarSystem.query.filter(
            SolarSystem.name.in_(ss_name_list)
        ).all()

        if solar_systems is None or len(solar_systems) == 0:
            return 'SolarSystems (%s) do not exist' % (solar_system_names), 404

        # put the solar system in a dict
        solar_systems_list = {}
        for system in solar_systems:
            solar_systems_list[system.id] = system.name

        # get the index from the list of solar system
        industry_index = IndustryIndex.query.filter(
            IndustryIndex.solarsystem_id.in_(solar_systems_list.keys()),
            IndustryIndex.activity == activity
        ).all()

        if industry_index is None or len(industry_index) == 0:
            return 'There is no index with SolarSystem(%s) or activity(%s)' % (
                solar_system_names,
                activity
            ), 404

        # and then put that index list into a dict[solar_system_name] = cost_index
        index_list = {}
        for index in industry_index:
            index_list[solar_systems_list[index.solarsystem_id]] = index.cost_index

        return jsonify(index=index_list)
    else:
        return 'This activity does not exist', 500
