# -*- encoding: utf-8 -*-
from flask.ext.login import LoginManager
from lazyblacksmith.models import EveUser


login_manager = LoginManager()
login_manager.login_view = 'sso.crest_login'

@login_manager.user_loader
def load_user(character_id):
    return EveUser.query.get(character_id)