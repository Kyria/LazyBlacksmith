# -*- encoding: utf-8 -*-
# local blueprints
from .home import home
from .template import template

# import blueprints from eve industry
from industry.blueprint import blueprint
from industry.price import price

# import ajax blueprint
from ajax.eve_api import ajax_eve_api
from ajax.eve_sde import ajax_eve_sde
from ajax.account import ajax_account

# user related stuff
from .user.account import account
from .user.sso import sso
