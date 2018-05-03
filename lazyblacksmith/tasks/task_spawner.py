# -*- encoding: utf-8 -*-
from .character.blueprints import task_update_character_blueprints
from .character.skills import task_update_character_skills
from .corporation.blueprints import task_update_corporation_blueprints
from .industry.indexes import task_update_industry_indexes
from .market.adjusted_price import task_update_adjusted_price
from .market.market_order import spawn_market_price_tasks

from lazyblacksmith.extension.celery_app import celery_app
from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_status
from lazyblacksmith.models import TaskState
from lazyblacksmith.models import TokenScope
from lazyblacksmith.models import db
from lazyblacksmith.utils.tasks import is_task_running
from lazyblacksmith.utils.time import utcnow

from . import logger

import datetime

CHAR_TASK_SCOPE = {
    TokenScope.SCOPE_SKILL: task_update_character_skills,
    TokenScope.SCOPE_CHAR_BLUEPRINTS: task_update_character_blueprints,
    TokenScope.SCOPE_CORP_BLUEPRINTS: task_update_corporation_blueprints,
}

UNIVERSE_TASKS = [
    task_update_adjusted_price,
    task_update_industry_indexes,
    spawn_market_price_tasks,
]


@celery_app.task(name="schedule.character_task_spawner")
def spawn_character_tasks():
    """ Task triggered every minutes that scan all tasks done to find
    any character based task to do (based on the cached_until field) """
    now = utcnow()

    # checking if API is up. If not, just stop it
    if not is_server_online():
        logger.info('Looks like EVE is still down / in VIP mode. Skipping !')
        return

    all_tokens = TokenScope.query.filter_by(valid=True).all()

    for token_scope in all_tokens:
        if skip_scope(token_scope):
            continue

        # check if there is no running task, and the data is not still cached
        if (not is_task_running(token_scope.user_id, token_scope.scope) and
                (not token_scope.cached_until or
                    token_scope.cached_until <= now)):

            task = CHAR_TASK_SCOPE[token_scope.scope]
            task_id = "%s-%s-%s" % (
                now.strftime('%Y%m%d-%H%M%S'),
                task.__name__,
                token_scope.user_id
            )
            token_state = TaskState(
                task_id=task_id,
                id=token_scope.user_id,
                scope=token_scope.scope,
            )
            db.session.add(token_state)
            db.session.commit()

            task.s(token_scope.user_id).apply_async(task_id=task_id)


@celery_app.task(name="schedule.universe_task_spawner")
def spawn_universe_tasks():
    """ Task triggered every XX minutes (not less than 5) that trigger
    'universe' tasks (market prices, industry indexes, ...) """
    now = utcnow()

    # checking if API is up. If not, just stop it
    if not is_server_online():
        logger.info('Looks like EVE is still down / in VIP mode. Skipping !')
        return

    for task in UNIVERSE_TASKS:
        if not is_task_running(None, task.__name__):
            task_id = "%s-%s" % (
                now.strftime('%Y%m%d-%H%M%S'),
                task.__name__,
            )
            token_state = TaskState(
                task_id=task_id,
                id=None,
                scope=task.__name__,
            )
            db.session.add(token_state)
            db.session.commit()

            task.s().apply_async(task_id=task_id)


def skip_scope(token_scope):
    """ Return True if we must skip that token_scope
    This function return True in the following cases:
    - The user didn't log in for more than 30days
    - The user didn't log in for more than 7days, and we already updated the
        token once today
    - the scope is not registered in the task scopes list
    - the scope has no tasks registered to it
    """
    yesterday = (utcnow() - datetime.timedelta(days=1))
    past_week = (utcnow() - datetime.timedelta(days=7))
    past_month = (utcnow() - datetime.timedelta(days=30))
    # if the user was not logged in the previous 7 days, update once/day
    # and if not logged from more than 30 days, don't update
    if token_scope.user.main_character is None:
        last_seen = token_scope.user.current_login_at
    else:
        last_seen = token_scope.user.main_character.current_login_at

    if last_seen < past_week:
        if last_seen < past_month:
            return True
        if not token_scope.last_update:
            return True
        if token_scope.last_update > yesterday:
            return True

    # if no task is defined for the scope, skip it
    if (token_scope.scope not in CHAR_TASK_SCOPE or
            CHAR_TASK_SCOPE[token_scope.scope] is None):
        return True

    # if nothing match, return False
    return False


def is_server_online():
    """ return true if server looks online, else otherwise """
    res = esiclient.request(get_status())
    return (res.status == 200 and 'vip' not in res.data)
