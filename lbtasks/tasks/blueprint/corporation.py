# -*- encoding: utf-8 -*-
""" Corporation blueprint task """
from sqlalchemy.exc import SQLAlchemyError

from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import (
    get_characters, get_characters_roles, get_corporations_blueprints)
from lazyblacksmith.models import Blueprint, TokenScope, User, db
from lazyblacksmith.utils.models import (get_token_update_esipy,
                                         inc_fail_token_scope,
                                         update_token_state)

from ... import celery_app, logger


@celery_app.task(name="update_corporation_blueprints")
def task_update_corporation_blueprints(character_id):
    """ Update the skills for a given character_id """

    character = User.query.get(character_id)
    if character is None:
        return

    # get token
    token = get_token_update_esipy(
        character_id=character_id,
        scope=TokenScope.SCOPE_CORP_BLUEPRINTS
    )

    # check char roles
    op = get_characters_roles(character_id=character_id)
    res = esiclient.request(op)
    if (res.status != 200 or
            (res.status == 200 and 'Director' not in res.data.roles)):
        inc_fail_token_scope(token, res.status)
        return

    character.is_corp_director = True

    # check char corporation
    op = get_characters(character_id=character_id)
    res = esiclient.request(op)
    if res.status != 200 and character.corporation_id is None:
        inc_fail_token_scope(token, res.status)
        return

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
        inc_fail_token_scope(token, bp_one.status_code)
        logger.error(
            'Request failed [%s, %s, %d]: %s',
            op_blueprint[0].url,
            op_blueprint[0].query,
            bp_one.status,
            bp_one.raw,
        )
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
    for _, response in [(op_blueprint[0], bp_one)] + bp_list:
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
                    corporation=True,
                )
                try:
                    db.session.add(blueprints[key])
                    db.session.commit()
                except SQLAlchemyError:
                    logger.exception(
                        "Error while trying to add blueprint id: %d",
                        item_id
                    )
                continue

            if not original:
                blueprints[key].total_runs += runs

    # delete every blueprint that have not been updated
    for key in (blueprint_init_list - blueprint_updated_list):
        db.session.delete(blueprints[key])
    try:
        db.session.commit()
    except SQLAlchemyError:
        logger.exception(
            "Error while trying to delete unused blueprints"
        )

    # update the token and the state
    update_token_state(token, bp_one.header['Expires'][0])
