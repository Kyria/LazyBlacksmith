# -*- encoding: utf-8 -*-
from flask_script import Command
from flask_script import Option

from lazyblacksmith.tasks.task_spawner import spawn_character_tasks
from lazyblacksmith.tasks.task_spawner import spawn_universe_tasks

class ManualCeleryTasks(Command):
    """ Manually trigger task spawner for celery.
    
    Arguments:
        -c|--character: triggers character related task spawner
        -u|--universe: triggers universe related task spawner (orders, indexes...)
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
    )

    def run(self, character, universe):
        if character:
            spawn_character_tasks()
        if universe:
            spawn_universe_tasks()