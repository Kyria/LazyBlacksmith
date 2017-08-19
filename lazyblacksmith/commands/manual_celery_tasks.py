# -*- encoding: utf-8 -*-
from flask_script import Command
from flask_script import Option

from lazyblacksmith.tasks.task_spawner import spawn_character_tasks
from lazyblacksmith.tasks.task_spawner import spawn_universe_tasks
from lazyblacksmith.tasks.purge import task_purge
from lazyblacksmith.models import TaskState, db
from lazyblacksmith.utils.time import utcnow


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
            spawn_character_tasks()
        if universe:
            spawn_universe_tasks()
        if purge:
            task_id = "%s-%s" % (
                utcnow().strftime('%Y%m%d-%H%M%S'),
                task_purge.__name__,
            )
            token_state = TaskState(
                task_id=task_id,
                id=None,
                scope=task_purge.__name__,
            )
            db.session.add(token_state)
            db.session.commit()

            task_purge.s().apply_async(task_id=task_id)
