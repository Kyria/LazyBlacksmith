# -*- encoding: utf-8 -*-
from flask import Blueprint
from flask import jsonify
from flask import request
from flask_login import current_user
from flask_login import login_required

from lazyblacksmith.models import db
from lazyblacksmith.models import TokenScope

import logging


logger = logging.getLogger('%s.views.ajax' % __name__)
ajax_account = Blueprint('ajax_account', __name__)


@ajax_account.route('/scopes/<int:character_id>/<scope>', methods=['DELETE'])
@login_required
def delete_scope(character_id, scope):
    if request.is_xhr:
        allowed_character_id = [
            alt.character_id for alt in current_user.alts_characters.all()
        ]
        if (character_id == current_user.character_id 
           or character_id in allowed_character_id):
            try:
                TokenScope.query.filter(
                    TokenScope.user_id == character_id,
                    TokenScope.scope == scope
                ).delete()
                db.session.commit()
                return jsonify({'status': 'success'})
                
            except:
                logger.exception('Cannot delete scope %s for user_id %s' % (
                    scope,
                    character_id,
                ))
                db.session.rollback()
                response = jsonify({
                    'status': 'error',
                    'message': 'Error while trying to delete scope'
                })
                response.status_code = 500
                return response
        else:
            response = jsonify({
                'status': 'error',
                'message': 'This character does not belong to you'
            })
            response.status_code = 500
            return response
    else:
        return 'Cannot call this page directly', 403
        

@ajax_account.route('/scopes/<character_id>/<scope>', methods=['POST'])
@login_required
def update_scope(character_id, scope):
    if request.is_xhr:
        allowed_character_id = [
            alt.character_id for alt in current_user.alts_characters.all()
        ]
        if (character_id == current_user.character_id 
           or character_id in allowed_character_id):
            response = jsonify({
                'status': 'error',
                'message': 'Not yet implemented !'
            })
            response.status_code = 500

        else:
            response = jsonify({
                'status': 'error',
                'message': 'This character does not belong to you'
            })
            response.status_code = 500
            return response
    else:
        return 'Cannot call this page directly', 403


@ajax_account.route('/user_preference/', methods=['POST'])
@login_required
def update_user_preference():
    if request.is_xhr:
        preferences = request.get_json()

        if 'production' in preferences:
            return update_production_preference(preferences['production'])

        if 'research' in preferences:
            return update_research_preference(preferences['research'])

        if 'invention' in preferences:
            return update_invention_preference(preferences['invention'])
    else:
        return 'Cannot call this page directly', 403


def update_production_preference(preferences):
    if preferences:
        pref = current_user.pref

        try:
            pref.prod_facility = preferences['facility']
            pref.prod_me_rig = preferences['meRig']
            pref.prod_te_rig = preferences['teRig']
            pref.prod_security = preferences['security']
            pref.prod_system = preferences['system']
            pref.prod_sub_facility = preferences['componentFacility']
            pref.prod_sub_me_rig = preferences['componentMeRig']
            pref.prod_sub_te_rig = preferences['componentTeRig']
            pref.prod_sub_security = preferences['componentSecurity']
            pref.prod_sub_system = preferences['componentSystem']
            pref.prod_price_region_minerals = preferences['priceMineralRegion']
            pref.prod_price_type_minerals = preferences['priceMineralType']
            pref.prod_price_region_pi = preferences['pricePiRegion']
            pref.prod_price_type_pi = preferences['pricePiType']
            pref.prod_price_region_moongoo = preferences['priceMoongooRegion']
            pref.prod_price_type_moongoo = preferences['priceMoongooType']
            pref.prod_price_region_others = preferences['priceOtherRegion']
            pref.prod_price_type_others = preferences['priceOtherType']

            db.session.commit()
            return jsonify({'status': 'success'})

        except:
            logger.exception('Cannot update preferences')
            db.session.rollback()
            response = jsonify({
                'status': 'error',
                'message': 'Error while updating preferences'
            })
            response.status_code = 500
            return response
    else:
        response = jsonify({
            'status': 'error',
            'message': 'Error: preferences are empty'
        })
        response.status_code = 500
        return response


def update_invention_preference(preferences):
    if preferences:
        pref = current_user.pref

        try:
            pref.invention_facility = preferences['facility']
            pref.invention_invention_rig = preferences['inventionRig']
            pref.invention_copy_rig = preferences['copyRig']
            pref.invention_security = preferences['security']
            pref.invention_system = preferences['system']
            pref.invention_price_region = preferences['priceRegion']
            pref.invention_price_type = preferences['priceType']

            db.session.commit()
            return jsonify({'status': 'success'})

        except:
            logger.exception('Cannot update preferences')
            db.session.rollback()
            response = jsonify({
                'status': 'error',
                'message': 'Error while updating preferences'
            })
            response.status_code = 500
            return response
    else:
        response = jsonify({
            'status': 'error',
            'message': 'Error: preferences are empty'
        })
        response.status_code = 500
        return response


def update_research_preference(preferences):
    if preferences:
        pref = current_user.pref

        try:
            pref.research_facility = preferences['facility']
            pref.research_me_rig = preferences['meRig']
            pref.research_te_rig = preferences['teRig']
            pref.research_copy_rig = preferences['copyRig']
            pref.research_security = preferences['security']
            pref.research_system = preferences['system']

            db.session.commit()
            return jsonify({'status': 'success'})

        except:
            logger.exception('Cannot update preferences')
            db.session.rollback()
            response = jsonify({
                'status': 'error',
                'message': 'Error while updating preferences'
            })
            response.status_code = 500
            return response
    else:
        response = jsonify({
            'status': 'error',
            'message': 'Error: preferences are empty'
        })
        response.status_code = 500
        return response
