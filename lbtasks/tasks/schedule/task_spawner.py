# -*- encoding: utf-8 -*-
""" Spawn all tasks if running manually in some cases """
import datetime

from lazyblacksmith.extension.esipy import esiclient
from lazyblacksmith.extension.esipy.operations import get_status
from lazyblacksmith.models import TokenScope
from lazyblacksmith.utils.time import utcnow
from lbtasks.tasks.blueprint.character import task_update_character_blueprints
from lbtasks.tasks.blueprint.corporation import \
    task_update_corporation_blueprints
from lbtasks.tasks.character.skills import task_update_character_skills
from lbtasks.tasks.universe.adjusted_prices import \
    task_adjusted_price_base_cost
from lbtasks.tasks.universe.indexes import task_industry_indexes
from lbtasks.tasks.universe.market_order import spawn_market_price_tasks

from ... import celery_app, logger

CHAR_TASK_SCOPE = {
    TokenScope.SCOPE_SKILL: task_update_character_skills,
    TokenScope.SCOPE_CHAR_BLUEPRINTS: task_update_character_blueprints,
    TokenScope.SCOPE_CORP_BLUEPRINTS: task_update_corporation_blueprints,
}

UNIVERSE_TASKS = [
    task_industry_indexes,
    task_adjusted_price_base_cost,
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
        if not token_scope.cached_until or token_scope.cached_until <= now:
            task = CHAR_TASK_SCOPE[token_scope.scope]
            task.delay(token_scope.user_id)


@celery_app.task(name="schedule.universe_task_spawner")
def spawn_universe_tasks():
    """ Task triggered every XX minutes (not less than 5) that trigger
    'universe' tasks (market prices, industry indexes, ...) """
    # checking if API is up. If not, just stop it
    if not is_server_online():
        logger.info('Looks like EVE is still down / in VIP mode. Skipping !')
        return

    for task in UNIVERSE_TASKS:
        task.delay()


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
