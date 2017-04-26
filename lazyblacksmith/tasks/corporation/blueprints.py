# -*- encoding: utf-8 -*-
from .. import logger
from ..lb_task import LbTask


from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esisecurity
from lazyblacksmith.models import Blueprint
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import User
from lazyblacksmith.models import db
from lazyblacksmith.utils.time import utcnow

import evelink.api
import evelink.char

from datetime import datetime

import pytz
import requests


@celery_app.task(name="update_corporation_blueprints", base=LbTask, bind=True)
def task_update_corporation_blueprints(self, character_id):
    """ Update the skills for a given character_id """
    self.start()

    character = User.query.get(character_id)
    if character is None:
        return

    # get token
    token = self.get_token_scope(
        user_id=character_id,
        scope=TokenScope.SCOPE_CORP_ASSETS
    )
    esisecurity.update_token(token.get_sso_data())

    # check if we need to update the token
    if esisecurity.is_token_expired():
        token.update_token(esisecurity.refresh())
        db.session.commit()

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

    try:
        # init evelink
        api = evelink.api.API(sso_token=(token.access_token, 'corporation'))
        corp = evelink.corp.Corp(api=api)
        api_bp_list = corp.blueprints()

        for blueprint in api_bp_list.result.values():
            original = blueprint['quantity'] != -2
            runs = blueprint['runs']
            me = blueprint['material_efficiency']
            te = blueprint['time_efficiency']
            item_id = blueprint['type_id']

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

        db.session.commit()

    except evelink.api.APIError as e:
        self.inc_fail_token_scope(token, e.code)
        logger.exception(e.message)
        self.end(TaskState.ERROR)
        return

    except requests.HTTPError as e:
        self.inc_fail_token_scope(token, e.response.status_code)
        logger.exception(e.message)
        self.end(TaskState.ERROR)
        return

    # update the token and the state
    token.request_try = 0
    token.last_update = utcnow()
    token.cached_until = datetime.fromtimestamp(
        api_bp_list.expires,
        tz=pytz.utc
    )
    db.session.commit()
    self.end(TaskState.SUCCESS)
