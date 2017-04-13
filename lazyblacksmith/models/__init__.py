# -*- encoding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# LB models
from .user.token_scope import TokenScope  # noqa
from .user.user import User  # noqa
from .user.user_preference import UserPreference  # noqa

# SDE models
from .sde.activity import Activity  # noqa
from .sde.activitymaterial import ActivityMaterial  # noqa
from .sde.activityproduct import ActivityProduct  # noqa
from .sde.activityskill import ActivitySkill  # noqa
from .sde.constellation import Constellation  # noqa
from .sde.decryptor import Decryptor  # noqa
from .sde.item import Item  # noqa
from .sde.orerefining import OreRefining  # noqa
from .sde.region import Region  # noqa
from .sde.solarsystem import SolarSystem  # noqa

# Tasks related models
from .tasks.task_state import TaskState  # noqa

# EVE API / universe models
from .api.industry_index import IndustryIndex  # noqa
from .api.item_adjusted_price import ItemAdjustedPrice  # noqa
from .api.item_price import ItemPrice  # noqa

# EVE API / Character models
from .character.blueprint import Blueprint  # noqa
from .character.skill import Skill  # noqa
