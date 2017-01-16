# -*- encoding: utf-8 -*-
from flask_login import LoginManager
from lazyblacksmith.models import User


login_manager = LoginManager()
login_manager.login_view = 'sso.login'


@login_manager.user_loader
def load_user(character_id):
    return User.query.get(character_id)
