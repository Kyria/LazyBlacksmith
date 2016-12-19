# -*- encoding: utf-8 -*-
from __future__ import absolute_import

from .esipy import esiapp

get_industry_systems = esiapp.op['get_industry_systems']
get_markets_prices = esiapp.op['get_markets_prices']

# require region_id, order_type=(all|buy|sell)
# optional: type_id, page
get_markets_region_id_orders = esiapp.op['get_markets_region_id_orders']
