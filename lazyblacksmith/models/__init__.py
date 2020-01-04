# -*- encoding: utf-8 -*-
""" Load all models here for migration ease """
# pylint: disable=unused-import
# flake8: noqa

from lazyblacksmith.extension.database import db

# LB models
from .user.token_scope import TokenScope
from .user.user import User
from .user.user_preference import UserPreference

# SDE models
from .sde.activity import Activity
from .sde.activitymaterial import ActivityMaterial
from .sde.activityproduct import ActivityProduct
from .sde.activityskill import ActivitySkill
from .sde.constellation import Constellation
from .sde.decryptor import Decryptor
from .sde.item import Item
from .sde.orerefining import OreRefining
from .sde.region import Region
from .sde.solarsystem import SolarSystem

# Tasks related models
from .tasks.task_state import TaskState

# EVE API / universe models
from .api.industry_index import IndustryIndex
from .api.item_adjusted_price import ItemAdjustedPrice
from .api.item_price import ItemPrice
from .api.market_order import MarketOrder

# EVE API / Character models
from .character.blueprint import Blueprint
from .character.skill import Skill
