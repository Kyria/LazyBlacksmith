# -*- encoding: utf-8 -*-
from flask import flash
from flask import session
from flask_login import login_user
from sqlalchemy.orm.exc import NoResultFound

from lazyblacksmith.models import EveUser
from lazyblacksmith.models import db

   
def check_login_user(character_data, auth_response, main=None):
    try:
        user = EveUser.query.filter(
            EveUser.character_id == character_data['CharacterID'],
            EveUser.character_owner_hash == character_data['CharacterOwnerHash']
        ).one()
        
    except NoResultFound:
        # if none is found, try to find just with characterID
        try:
            user = EveUser.query.filter(
                EveUser.character_id == character_data['CharacterID'],
            ).one()
            # if no exception is triggered, it mean we have a registered charID
            # but with another account: owner has changed, we'll wipe all data.
            wipe_character_data(user)
            
        except NoResultFound:
            user = EveUser()
            user.character_id = character_data['CharacterID']
    
    user.character_owner_hash = character_data['CharacterOwnerHash']
    user.character_name = character_data['CharacterName']
    user.update_token(auth_response)
    
    if main is not None:
        user.main_character = main
    
    try:
        db.session.merge(user)
        db.session.commit()
        
        if main is None:
            login_user(user)
            flash('You were successfully logged in')
        else:
            flash(
                'You successfully added "%s" to your alts' % (
                    user.character_name,
                )
            )
    except:
        db.session.rollback()
        flash('Something went wrong. Please contact the administrator')
        
        
def wipe_character_data(user):
    # there is nothing to wipe yet
    pass
        