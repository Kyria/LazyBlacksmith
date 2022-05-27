# -*- encoding: utf-8 -*-
""" Manually trigger task spawner for celery.

Arguments:
    -c|--character: triggers character related task spawner
    -u|--universe: triggers universe related task spawner
    -p|--purge: purge old data task
"""
import click
from flask.cli import with_appcontext

from lbtasks.tasks import (spawn_character_tasks, spawn_universe_tasks,
                           task_purge)

# pylint: disable=method-hidden,arguments-differ
@click.command('celery_tasks')
@click.option('-c', '--character',
              is_flag=True,
              default=False,
              help='Trigger character tasks spawner')
@click.option('-u', '--universe',
              is_flag=True,
              default=False,
              help='Trigger universe tasks spawner (market order, indexes...)')
@click.option('-p', '--purge',
              is_flag=True,
              default=False,
              help='Launch the purge task')
@with_appcontext
def celery_tasks(character, universe, purge):
    if character:
        spawn_character_tasks.delay()
    if universe:
        spawn_universe_tasks.delay()
    if purge:
        task_purge.delay()
