from collections import OrderedDict
from flask import abort
from flask import Blueprint
from flask import json
from flask import jsonify
from flask import render_template
from flask import request
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound

from lazyblacksmith.models import Item
from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivityProduct
from lazyblacksmith.models import ActivityMaterial
from lazyblacksmith.models import SolarSystem

ajax = Blueprint('ajax', __name__)

@ajax.route('/blueprint/search/<string:name>', methods=['GET'])
def blueprint_search(name):
    """
    Return JSON result for a specific search
    name is the request name.
    """
    if request.is_xhr:
        #cache_key = 'blueprint:search:%s' % (name.lower().replace(" ", ""),)

        data = None #cache.get(cache_key)
        if data is None:
            blueprints = Item.query.filter(Item.name.ilike('%'+name.lower()+'%'), Item.max_production_limit.isnot(None)).order_by(Item.name.asc()).all()

            data = []
            for bp in blueprints: 
                invention = 0
                
                ## we are taking the first activity as we cannot have RE and invention at the same time
                #for pa in ActivityProduct.objects.filter(product_id = bp.item_id):
                #    if pa.activity == Activity.ACTIVITY_INVENTION:
                #        invention = 1
                #        break
                        
                data.append([bp.id, bp.name, invention])
            
            # cache for 7 day as it does not change that often
            #cache.set(cache_key, json.dumps(data), 24*3600*7)

        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403


@ajax.route('/blueprint/bom/<int:blueprint_id>', methods=['GET'])
def blueprint_bom(blueprint_id):
    """
    Return JSON with the list of all bill of material for
    each material in the blueprint given in argument
    """
    if request.is_xhr:
        #cache_key = 'blueprint:matbom:%s' % item_id
    
        data = None #cache.get(cache_key)
        if data is None:
            blueprints = ActivityMaterial.query.filter_by(item_id=blueprint_id, activity=Activity.ACTIVITY_MANUFACTURING).all()

            data = OrderedDict()
            for bp in blueprints:

                # As all item cannot be manufactured, catch the exception 
                try:
                    bp_final = bp.material.product_for_activities
                    bp_final = bp_final.filter_by(activity=Activity.ACTIVITY_MANUFACTURING).one()
                    bp_final = bp_final.blueprint
                except NoResultFound:
                    continue

                mats = bp_final.activity_materials.filter_by(activity=Activity.ACTIVITY_MANUFACTURING).all()

                if bp_final.id not in data:
                    data[bp_final.id] = {
                        'id':bp.material.id,
                        'icon':bp_final.icon_32(),
                        'name':bp_final.name,
                        'materials':[],
                    }

                for mat in mats:
                    data[bp_final.id]['materials'].append({
                        'id':mat.material.id,
                        'name':mat.material.name,
                        'quantity':mat.quantity,
                        'icon':mat.material.icon_32(),
                    })

        return jsonify(result=data)
    else:
        return 'Cannot call this page directly', 403


@ajax.route('/solarsystem/list', methods=['GET'])
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

#if request.is_ajax():
#cache_key = 'system:list'
#data = cache.get(cache_key)
#if data is None:
#systems = System.objects.all()
#data = []
#for system in systems:
#data.append(system.name)
## cache for 1 day as it does not change that often
#data = json.dumps(data)
#cache.set(cache_key, data, 24*3600*7)
#return HttpResponse(data, content_type='application/json')
#else:
#return HttpResponse(content='Cannot call this page directly', status=403)#