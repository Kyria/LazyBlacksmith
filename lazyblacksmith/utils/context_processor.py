# -*- encoding: utf-8 -*-
from flask import g
import lazyblacksmith.models.enums as enums

def inject_user():
    """ inject the user into the context for flask_login """
    try:
        return {'user': g.user}
    except AttributeError:
        return {'user': None}
        
def inject_enums():
    """ inject the enums into the context """
    return {
        'ActivityEnum': enums.ActivityEnum,
        'BlueprintEnum': enums.BlueprintEnum,
    }