# -*- encoding: utf-8 -*-
from .. import logger
from ..lb_task import LbTask


from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_characters
from lazyblacksmith.extension.esipy.operations import get_characters_roles
from lazyblacksmith.extension.esipy.operations import get_corporations_blueprints
from lazyblacksmith.models import Blueprint
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import User
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

from datetime import datetime
from email.utils import parsedate

import pytz


@celery_app.task(name="update_corporation_blueprints", base=LbTask, bind=True)
def task_update_corporation_blueprints(self, character_id):
    """ Update the skills for a given character_id """
    self.start()

    character = User.query.get(character_id)
    if character is None:
        return

    # get token
    token = self.get_token_update_esipy(
        character_id=character_id,
        scope=TokenScope.SCOPE_CORP_BLUEPRINTS
    )

    # check char roles
    op = get_characters_roles(character_id=character_id)
    res = esiclient.request(op)
    if res.status != 200 or (res.status == 200 and 'Director' not in res.data.roles):
        self.inc_fail_token_scope(token, res.status)
        return self.end(TaskState.FAILURE)

    character.is_corp_director = True

    # check char corporation
    op = get_characters(character_id=character_id)
    res = esiclient.request(op)
    if res.status != 200 and character.corporation_id is None:
        self.inc_fail_token_scope(token, res.status)
        return self.end(TaskState.FAILURE)

    character.corporation_id = res.data.corporation_id

    # get current blueprints
    bps = Blueprint.query.filter_by(
        character_id=character_id
    ).filter_by(
        corporation=True
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
    op_blueprint = get_corporations_blueprints(
        corporation_id=character.corporation_id,
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
        operations.append(get_corporations_blueprints(
            corporation_id=character.corporation_id,
            page=page
        ))

    # query all other pages and add the first page
    bp_list = esiclient.multi_request(operations)

    # parse the response and save everything
    for req, response in [(op_blueprint[0], bp_one)] + bp_list:

        original = (response.data.quantity != -2)
        runs = response.data.runs
        me = response.data.material_efficiency
        te = response.data.time_efficiency
        item_id = response.data.type_id

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
                corporation=True,
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
