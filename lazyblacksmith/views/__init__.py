# -*- encoding: utf-8 -*-
# local blueprints
from .home import home
from .sso import sso
from .template import template

# import blueprints from eve industry
from industry.blueprint import blueprint
from industry.price import price

# import ajax blueprint
from ajax.eve_api import ajax_eve_api
from ajax.eve_sde import ajax_eve_sde
