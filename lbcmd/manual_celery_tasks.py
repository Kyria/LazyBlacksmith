# -*- encoding: utf-8 -*-
from flask_script import Command, Option

from lbtasks.tasks import task_purge
from lbtasks.tasks.task_spawner import (spawn_character_tasks,
                                        spawn_universe_tasks)


class ManualCeleryTasks(Command):
    """ Manually trigger task spawner for celery.

    Arguments:
        -c|--character: triggers character related task spawner
        -u|--universe: triggers universe related task spawner (orders, indexes...)
        -p|--purge: purge old data task
    """

    option_list = (
        Option(
            '--character', '-c',
            dest='character',
            action="store_true",
            default=False,
            help=('Trigger character tasks spawner')
        ),
        Option(
            '--universe', '-u',
            dest='universe',
            action="store_true",
            default=False,
            help=('Trigger universe tasks spawner (market order, indexes...)')
        ),
        Option(
            '--purge', '-p',
            dest='purge',
            action="store_true",
            default=False,
            help=('Launch the purge task')
        ),
    )

    def run(self, character, universe, purge):
        if character:
            spawn_character_tasks.delay()
        if universe:
            spawn_universe_tasks.delay()
        if purge:
            task_purge.delay()
