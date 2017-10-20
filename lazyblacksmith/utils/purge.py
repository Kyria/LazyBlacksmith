# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from flask_login import logout_user
from lazyblacksmith.models import Blueprint
from lazyblacksmith.models import Skill
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import User
from lazyblacksmith.models import UserPreference
from lazyblacksmith.models import db


def purge_characters_skill(user):
    """ purge the skill from all character belonging to a given user"""

    # remove the main char skills
    Skill.query.filter(Skill.character_id == user.character_id).delete()

    alts = [alt.character_id for alt in user.alts_characters.all()]
    # remove all alt skills
    if alts:
        Skill.query.filter(
            Skill.character_id.in_(alts)
        ).delete(synchronize_session='fetch')

    # commit
    db.session.commit()


def purge_characters_blueprints(user):
    """ purge blueprints from all character belonging to a given user"""

    # remove the main char skills
    Blueprint.query.filter(
        Blueprint.character_id == user.character_id
    ).filter_by(corporation=False).delete()

    alts = [alt.character_id for alt in user.alts_characters.all()]
    # remove all alt skills
    if alts:
        Blueprint.query.filter(
            Blueprint.character_id.in_(alts)
        ).filter_by(corporation=False).delete(synchronize_session='fetch')

    # commit
    db.session.commit()


def purge_corporation_blueprints(user):
    """ purge blueprints from all character belonging to a given user"""

    # remove the main char skills
    Blueprint.query.filter(
        Blueprint.character_id == user.character_id
    ).filter_by(corporation=True).delete()

    alts = [alt.character_id for alt in user.alts_characters.all()]
    # remove all alt skills
    if alts:
        Blueprint.query.filter(
            Blueprint.character_id.in_(alts)
        ).filter_by(corporation=True).delete(synchronize_session='fetch')

    # commit
    db.session.commit()


def delete_account(user):
    """ Remove all data and account from the database of a given user """
    purge_characters_skill(user)
    purge_characters_blueprints(user)
    purge_corporation_blueprints(user)

    alts = [alt.character_id for alt in user.alts_characters.all()]

    # remove preferences
    UserPreference.query.filter(
        UserPreference.user_id == user.character_id
    ).delete()

    # remove scopes
    TokenScope.query.filter(
        TokenScope.user_id == user.character_id
    ).delete()

    # delete all alts stuff
    if alts:
        TokenScope.query.filter(
            TokenScope.user_id.in_(alts)
        ).delete(synchronize_session='fetch')

        User.query.filter(
            User.character_id.in_(alts)
        ).delete(synchronize_session='fetch')

    # commit
    db.session.commit()

    user_id = user.character_id

    # logout user
    logout_user()

    # remove current user from database
    User.query.filter_by(character_id=user_id).delete()

    # commit
    db.session.commit()
