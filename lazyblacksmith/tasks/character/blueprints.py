# -*- encoding: utf-8 -*-
from .. import logger
from ..lb_task import LbTask

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_characters_blueprints
from lazyblacksmith.models import Blueprint
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import User
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from datetime import datetime
from email.utils import parsedate

import pytz


@celery_app.task(name="update_character_blueprints", base=LbTask, bind=True)
def task_update_character_blueprints(self, character_id):
    """ Update the skills for a given character_id """
    self.start()

    character = User.query.get(character_id)
    if character is None:
        return

    # get token
    token = self.get_token_update_esipy(
        character_id=character_id,
        scope=TokenScope.SCOPE_CHAR_BLUEPRINTS
    )

    # get current blueprints
    bps = Blueprint.query.filter_by(
        character_id=character_id
    ).filter_by(
        corporation=False
    ).all()
    blueprints = {}

    for bp in bps:
        key = "%s-%d-%d-%d" % (
            bp.item_id,
            bp.original,
            bp.material_efficiency,
            bp.time_efficiency
        )
        # update run to 0, to have the real total run for bpc
        if not bp.original:
            bp.total_runs = 0
        blueprints[key] = bp

    # set of known blueprints
    blueprint_init_list = set(blueprints.keys())
    blueprint_updated_list = set()

    # get the first page to have the page number
    op_blueprint = get_characters_blueprints(
        character_id=character_id,
        page=1
    )

    bp_one = esiclient.request(op_blueprint)

    if bp_one.status != 200:
        logger.error('Request failed [%s, %s, %d]: %s' % (
            op_blueprint[0].url,
            op_blueprint[0].query,
            bp_one.status,
            bp_one.raw,
        ))
        self.end(TaskState.ERROR)
        return

    # prepare all other pages
    total_page = bp_one.header['X-Pages'][0]
    operations = []
    for page in range(2, total_page + 1):
        operations.append(get_characters_blueprints(
            character_id=character_id,
            page=page
        ))

    # query all other pages and add the first page
    bp_list = esiclient.multi_request(operations)

    # parse the response and save everything
    for req, response in [(op_blueprint[0], bp_one)] + bp_list:
        for blueprint in response.data:

            original = (blueprint.quantity != -2)
            runs = blueprint.runs
            me = blueprint.material_efficiency
            te = blueprint.time_efficiency
            item_id = blueprint.type_id

            key = "%s-%d-%d-%d" % (item_id, original, me, te)

            if key not in blueprint_updated_list:
                blueprint_updated_list.add(key)

            if key not in blueprints:
                blueprints[key] = Blueprint(
                    item_id=item_id,
                    original=original,
                    total_runs=runs,
                    material_efficiency=me,
                    time_efficiency=te,
                    character_id=character_id,
                )
                db.session.add(blueprints[key])
                continue

            if not original:
                blueprints[key].total_runs += runs

    # delete every blueprint that have not been updated
    for key in (blueprint_init_list - blueprint_updated_list):
        db.session.delete(blueprints[key])

    # update the token and the state
    token.request_try = 0
    token.last_update = utcnow()
    token.cached_until = datetime(
        *parsedate(bp_one.header['Expires'][0])[:6]
    ).replace(tzinfo=pytz.utc)
    db.session.commit()
    self.end(TaskState.SUCCESS)
