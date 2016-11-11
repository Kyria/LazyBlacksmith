# -*- encoding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .eve_sde.activity import Activity  # noqa
from .eve_sde.activitymaterial import ActivityMaterial  # noqa
from .eve_sde.activityproduct import ActivityProduct  # noqa
from .eve_sde.activityskill import ActivitySkill  # noqa
from .eve_sde.constellation import Constellation  # noqa
from .eve_sde.decryptor import Decryptor  # noqa
from .eve_sde.item import Item  # noqa
from .eve_sde.orerefining import OreRefining  # noqa
from .eve_sde.region import Region  # noqa
from .eve_sde.solarsystem import SolarSystem  # noqa

from .crest.industry_index import IndustryIndex  # noqa
from .crest.item_adjusted_price import ItemAdjustedPrice  # noqa
from .crest.item_price import ItemPrice  # noqa

from .sso.eveuser import EveUser  # noqa
