# -*- encoding: utf-8 -*-
from collections import OrderedDict

from flask import Blueprint
from flask import json
from flask import jsonify
from flask import request
from sqlalchemy.orm.exc import NoResultFound

from . import is_not_ajax
from lazyblacksmith.extension.cache import cache
from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivityMaterial
from lazyblacksmith.models import Item
from lazyblacksmith.models import SolarSystem
from lazyblacksmith.utils.time import utcnow

import humanize

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
                Item.name.ilike('%'+name.lower()+'%'),
                Item.max_production_limit.isnot(None)
            ).order_by(
                Item.name.asc()
            ).all()

            data = []
            for bp in blueprints:
                invention = False
                # TODO: check if this can be invented.

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


@ajax_eve_sde.route('/blueprint/bom/<int:blueprint_id>', methods=['GET'])
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


@ajax_eve_sde.route('/solarsystem/list', methods=['GET'])
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
                Item.name.ilike('%'+name.lower()+'%'),
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
            cache.set(cache_key, json.dumps(data), 24*3600*7)

        else:
            data = json.loads(data)

        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403
