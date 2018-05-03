# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from .esipy import esiapp

# universe / api endpoints
get_status = esiapp.get_v1_swagger.op['get_status']
get_industry_systems = esiapp.get_v1_swagger.op['get_industry_systems']
get_markets_prices = esiapp.get_v1_swagger.op['get_markets_prices']
get_markets_region_id_orders = esiapp.get_v1_swagger.op['get_markets_region_id_orders']

# character endpoints
get_characters = esiapp.get_v4_swagger.op['get_characters_character_id']
get_characters_skills = esiapp.get_v4_swagger.op['get_characters_character_id_skills']
get_characters_blueprints = esiapp.get_v2_swagger.op['get_characters_character_id_blueprints']

# corporation related endpoints
get_characters_roles = esiapp.get_v2_swagger.op['get_characters_character_id_roles']
get_corporations_blueprints = esiapp.get_v1_swagger.op['get_corporations_corporation_id_blueprints']
