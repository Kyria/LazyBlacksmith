# -*- encoding: utf-8 -*-
# flake8: noqa
""" import all tasks here for easier use """

from .universe.indexes import task_industry_indexes
from .universe.adjusted_prices import task_adjusted_price_base_cost
from .universe.market_order import spawn_market_price_tasks
from .universe.market_order import task_update_region_order_price

from .character.skills import task_update_character_skills

from .blueprint.character import task_update_character_blueprints
from .blueprint.corporation import task_update_corporation_blueprints

from .schedule.purge import task_purge
from .schedule.task_spawner import spawn_character_tasks
from .schedule.task_spawner import spawn_universe_tasks
